import logging
import os
from pathlib import Path
from typing import Literal, Optional, Tuple, TypedDict

import numpy as np
import seekpath
from ase import Atoms, io
from ase.build import bulk, surface
from ase.io import read, write
from ase.optimize import BFGS
from deepmd.calculator import DP
from dp.agent.server import CalculationMCPServer
from phonopy import Phonopy
from phonopy.harmonic.dynmat_to_fc import get_commensurate_points
from phonopy.structure.atoms import PhonopyAtoms
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

### CONSTANTS
DEFAULT_HEAD = "MP_traj_v024_alldata_mixu"
THz_TO_K = 47.9924  # 1 THz ≈ 47.9924 K

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

mcp = CalculationMCPServer(
    "DPACalculatorServer", 
    host="0.0.0.0", 
    port=50001
)


class OptimizationResult(TypedDict):
    """Result structure for structure optimization"""
    optimized_structure: Path
    optimization_traj: Optional[Path]
    final_energy: float
    message: str


class PhononResult(TypedDict):
    """Result structure for phonon calculation"""
    entropy: float
    free_energy: float
    heat_capacity: float
    max_frequency_THz: float
    max_frequency_K: float
    band_plot: Path
    band_yaml: Path
    band_dat: Path


class BuildStructureResult(TypedDict):
    """Result structure for crystal structure building"""
    structure_file: Path


def prim2conven(ase_atoms: Atoms) -> Atoms:
    """
    Convert a primitive cell (ASE Atoms) to a conventional standard cell using pymatgen.
    Parameters:
        ase_atoms (ase.Atoms): Input primitive cell.
    Returns:
        ase.Atoms: Conventional cell.
    """
    structure = AseAtomsAdaptor.get_structure(ase_atoms)
    analyzer = SpacegroupAnalyzer(structure, symprec=1e-3)
    conven_structure = analyzer.get_conventional_standard_structure()
    conven_atoms = AseAtomsAdaptor.get_atoms(conven_structure)
    return conven_atoms


@mcp.tool()
def build_structure(
    structure_type: str,          
    material1: str,
    conventional: bool = True,
    crystal_structure1: str = 'fcc',
    a1: float = None,             
    b1: float = None,
    c1: float = None,
    alpha1: float = None,
    output_file: str = "structure.cif",
    miller_index1 = (1, 0, 0),    
    layers1: int = 4,
    vacuum1: float = 10.0,
    material2: str = None,        
    crystal_structure2: str = 'fcc',
    a2: float = None,
    b2: float = None,
    c2: float = None,
    alpha2: float = None,
    miller_index2 = (1, 0, 0),    
    layers2: int = 3,
    vacuum2: float = 10.0,
    stack_axis: int = 2,         
    interface_distance: float = 2.5,
    max_strain: float = 0.05,
) -> BuildStructureResult:
    """
    Build a crystal structure using ASE. Supports bulk crystals, surfaces, and interfaces.
    
    Args:
        structure_type (str): Type of structure to build. Allowed values: 'bulk', 'surface', 'interface'
        material1 (str): Element or chemical formula of the first material.
        conventional (bool): If True, convert primitive cell to conventional standard cell. Default True.
        crystal_structure1 (str): Crystal structure type for material1. Must be one of sc, fcc, bcc, tetragonal, bct, hcp, rhombohedral, orthorhombic, mcl, diamond, zincblende, rocksalt, cesiumchloride, fluorite or wurtzite. Default 'fcc'.
        a1 (float): Lattice constant a for material1. Default is ASE's default.
        b1 (float): Lattice constant b for material1. Only needed for non-cubic structures.
        c1 (float): Lattice constant c for material1. Only needed for non-cubic structures.
        alpha1 (float): Alpha angle in degrees. Only needed for non-cubic structures.   
        output_file (str): File path to save the generated structure (e.g., .cif). Default 'structure.cif'.
        miller_index1 (tuple of 3 integers): Miller index for surface orientation. Must be a tuple of exactly 3 integers. Default (1, 0, 0).
        layers1 (int): Number of atomic layers in slab. Default 4.
        vacuum1 (float): Vacuum spacing in Ångströms. Default 10.0.
        material2 (str): Second material (required for interface). Default None.
        crystal_structure2 (str): Crystal structure type for material2. Must be one of sc, fcc, bcc, tetragonal, bct, hcp, rhombohedral, orthorhombic, mcl, diamond, zincblende, rocksalt, cesiumchloride, fluorite or wurtzite. Default 'fcc'.
        a2 (float): Lattice constant a for material2. Default is ASE's default.
        b2 (float): Lattice constant b for material2. Only needed for non-cubic structures.
        c2 (float): Lattice constant c for material2. Only needed for non-cubic structures.
        alpha2 (float): Alpha angle in degrees. Only needed for non-cubic structures.
        miller_index2 (tuple): Miller index for material2 surfaceorientation. Must be a tuple of exactly 3 integers. Default (1, 0, 0).
        layers2 (int): Number of atomic layers in material2 slab. Default 3.
        vacuum2 (float): Vacuum spacing for material2. Default 10.0.
        stack_axis (int): Axis (0=x, 1=y, 2=z) for stacking. Default 2 (z-axis).
        interface_distance (float): Distance between surfaces in Å. Default 2.5.
        max_strain (float): Maximum allowed relative lattice mismatch. Default 0.05.
    
    Returns:
        dict: A dictionary containing:
            - structure_file (Path): Path to the generated structure file
    """
    try:
        if structure_type == 'bulk':
            atoms = bulk(material1, crystal_structure1, a=a1, b=b1, c=c1, alpha=alpha1)
            if conventional:
                atoms = prim2conven(atoms)

        elif structure_type == 'surface':        
            bulk1 = bulk(material1, crystal_structure1, a=a1, b=b1, c=c1, alpha=alpha1)
            atoms = surface(bulk1, miller_index1, layers1, vacuum=vacuum1)

        elif structure_type == 'interface':
            if material2 is None:
                raise ValueError("material2 must be specified for interface structure.")
            
            # Build surfaces
            bulk1 = bulk(material1, crystal_structure1, 
                        a=a1, b=b1, c=c1, alpha=alpha1)
            bulk2 = bulk(material2, crystal_structure2,
                        a=a2, b=b2, c=c2, alpha=alpha2)
            if conventional:
                bulk1 = prim2conven(bulk1)
                bulk2 = prim2conven(bulk2)
            surf1 = surface(bulk1, miller_index1, layers1)
            surf2 = surface(bulk2, miller_index2, layers2)
            # Align surfaces along the stacking axis
            axes = [0, 1, 2]
            axes.remove(stack_axis)
            axis1, axis2 = axes
            # Get in-plane lattice vectors
            cell1 = surf1.cell
            cell2 = surf2.cell
            # Compute lengths of in-plane lattice vectors
            len1_a = np.linalg.norm(cell1[axis1])
            len1_b = np.linalg.norm(cell1[axis2])
            len2_a = np.linalg.norm(cell2[axis1])
            len2_b = np.linalg.norm(cell2[axis2])
            # Compute strain to match lattice constants
            strain_a = abs(len1_a - len2_a) / ((len1_a + len2_a) / 2)
            strain_b = abs(len1_b - len2_b) / ((len1_b + len2_b) / 2)
            if strain_a > max_strain or strain_b > max_strain:
                raise ValueError(f"Lattice mismatch too large: strain_a={strain_a:.3f}, strain_b={strain_b:.3f}")
            # Adjust surf2 to match surf1's in-plane lattice constants
            scale_a = len1_a / len2_a
            scale_b = len1_b / len2_b
            # Scale surf2 cell
            new_cell2 = cell2.copy()
            new_cell2[axis1] *= scale_a
            new_cell2[axis2] *= scale_b
            surf2.set_cell(new_cell2, scale_atoms=True)
            # Shift surf2 along stacking axis
            max1 = max(surf1.positions[:, stack_axis])
            min2 = min(surf2.positions[:, stack_axis])
            shift = max1 - min2 + interface_distance
            surf2.positions[:, stack_axis] += shift
            # Combine surfaces
            atoms = surf1 + surf2
            # Add vacuum
            atoms.center(vacuum=vacuum1 + vacuum2, axis=stack_axis)
        else:
            raise ValueError(f"Unsupported structure_type: {structure_type}")
        # Save the structure
        write(output_file, atoms)
        logging.info(f"Structure saved to: {output_file}")
        return {
            "structure_file": Path(output_file)
        }
    except Exception as e:
        logging.error(f"Structure building failed: {str(e)}", exc_info=True)
        return {
            "structure_file": Path(""),
            "message": f"Structure building failed: {str(e)}"
        }



@mcp.tool()
def optimize_crystal_structure( 
    input_structure: Path,
    model_path: Path,
    force_tolerance: float = 0.01, 
    max_iterations: int = 100, 
) -> OptimizationResult:
    # TODO: RELAX CELL
    """Optimize crystal structure using a Deep Potential (DP) model.

    Args:
        input_structure (Path): Path to the input structure file (e.g., CIF, POSCAR).
        model_path (Path): Path to the trained Deep Potential model directory.
            Default is "bohrium://13756/27666/store/upload/d7af9d6c-ae70-40b5-a85b-1a62269946b8/dpa-2.4-7M.pt", i.e. the DPA-2.4-7M.
        force_tolerance (float, optional): Convergence threshold for atomic forces in eV/Å.
            Default is 0.01 eV/Å.
        max_iterations (int, optional): Maximum number of geometry optimization steps.
            Default is 100 steps.

    Returns:
        dict: A dictionary containing optimization results:
            - optimized_structure (Path): Path to the final optimized structure file.
            - optimization_traj (Optional[Path]): Path to the optimization trajectory file, if available.
            - final_energy (float): Final potential energy after optimization in eV.
            - message (str): Status or error message describing the outcome.
    """
    try:
        model_file = str(model_path)
        base_name = input_structure.stem
        
        logging.info(f"Reading structure from: {input_structure}")
        atoms = read(str(input_structure))
        atoms.calc = DP(model=model_file, head=DEFAULT_HEAD)

        traj_file = f"{base_name}_optimization_traj.extxyz"  
        if Path(traj_file).exists():
            logging.warning(f"Overwriting existing trajectory file: {traj_file}")
            Path(traj_file).unlink()

        logging.info("Starting structure optimization...")
        optimizer = BFGS(atoms, trajectory=traj_file)
        optimizer.run(fmax=force_tolerance, steps=max_iterations)

        output_file = f"{base_name}_optimized.cif"
        write(output_file, atoms)
        final_energy = atoms.get_potential_energy()

        logging.info(
            f"Optimization completed in {optimizer.nsteps} steps. "
            f"Final energy: {final_energy:.4f} eV"
        )

        return {
            "optimized_structure": Path(output_file),
            "optimization_traj": Path(traj_file),
            "final_energy": final_energy,
            "message": f"Successfully completed in {optimizer.nsteps} steps"
        }

    except Exception as e:
        logging.error(f"Optimization failed: {str(e)}", exc_info=True)
        return {
            "optimized_structure": Path(""),
            "optimization_traj": None, 
            "final_energy": -1.0,
            "message": f"Optimization failed: {str(e)}"
        }


@mcp.tool()
def calculate_phonon(
    cif_file: Path,
    model_path: Path,
    supercell_matrix: list[int] = [3,3,3],
    displacement_distance: float = 0.005,
    temperatures: tuple = (300,),
    plot_path: str = "phonon_band.png"
) -> PhononResult:
    """Calculate phonon properties using a Deep Potential (DP) model.

    Args:
        cif_file (Path): Path to the input CIF structure file.
        model_path (Path): Path to the Deep Potential model file.
            Default is "bohrium://13756/27666/store/upload/d7af9d6c-ae70-40b5-a85b-1a62269946b8/dpa-2.4-7M.pt", i.e. the DPA-2.4-7M.
        supercell_matrix (list[int], optional): 3×3 matrix for supercell expansion.
            Defaults to [3,3,3].
        displacement_distance (float, optional): Atomic displacement distance in Ångström.
            Default is 0.005 Å.
        temperatures (tuple, optional): Tuple of temperatures (in Kelvin) for thermal property calculations.
            Default is (300,).
        plot_path (str, optional): File path to save the phonon band structure plot.
            Default is "phonon_band.png".

    Returns:
        dict: A dictionary containing phonon properties:
            - entropy (float): Phonon entropy at given temperature [J/mol·K].
            - free_energy (float): Helmholtz free energy [kJ/mol].
            - heat_capacity (float): Heat capacity at constant volume [J/mol·K].
            - max_frequency_THz (float): Maximum phonon frequency in THz.
            - max_frequency_K (float): Maximum phonon frequency in Kelvin.
            - band_plot (str): File path to the generated band structure plot.
            - band_yaml (str): File path to the band structure data in YAML format.
            - band_dat (str): File path to the band structure data in DAT format.
    """

    if supercell_matrix is None or len(supercell_matrix) == 0:
        supercell_matrix = [3,3,3]

    try:
        # Read input files
        atoms = io.read(str(cif_file))
        
        # Convert to Phonopy structure
        ph_atoms = PhonopyAtoms(
            symbols=atoms.get_chemical_symbols(),
            cell=atoms.get_cell(),
            scaled_positions=atoms.get_scaled_positions()
        )
        
        # Setup phonon calculation
        phonon = Phonopy(ph_atoms, supercell_matrix)
        phonon.generate_displacements(distance=displacement_distance)
        
        # Calculate forces using DP model
        from deepmd.calculator import DP
        dp_calc = DP(model=str(model_path), head=DEFAULT_HEAD)
        
        force_sets = []
        for sc in phonon.supercells_with_displacements:
            sc_atoms = Atoms(
                cell=sc.cell,
                symbols=sc.symbols,
                scaled_positions=sc.scaled_positions,
                pbc=True
            )
            sc_atoms.calc = dp_calc
            force = sc_atoms.get_forces()
            force_sets.append(force - np.mean(force, axis=0))
            
        phonon.forces = force_sets
        phonon.produce_force_constants()
        
        # Calculate thermal properties
        phonon.run_mesh([10, 10, 10])
        phonon.run_thermal_properties(temperatures=temperatures)
        thermal = phonon.get_thermal_properties_dict()
        
        comm_q = get_commensurate_points(phonon.supercell_matrix)
        freqs = np.array([phonon.get_frequencies(q) for q in comm_q])

        
        base = Path(plot_path)
        base_path = base.with_suffix("")
        band_yaml_path = base_path.with_name(base_path.name + "_band.yaml")
        band_dat_path = base_path.with_name(base_path.name + "_band.dat")

        phonon.auto_band_structure(
            npoints=101,
            write_yaml=True,
            filename=str(band_yaml_path)
        )

        plot = phonon.plot_band_structure()
        plot.savefig(plot_path, dpi=300)


        return {
            "entropy": float(thermal['entropy'][0]),
            "free_energy": float(thermal['free_energy'][0]),
            "heat_capacity": float(thermal['heat_capacity'][0]),
            "max_frequency_THz": float(np.max(freqs)),
            "max_frequency_K": float(np.max(freqs) * THz_TO_K),
            "band_plot": Path(plot_path),
            "band_yaml": band_yaml_path,
            "band_dat": band_dat_path
        }
        
    except Exception as e:
        logging.error(f"Phonon calculation failed: {str(e)}", exc_info=True)
        return {
            "entropy": -1.0,
            "free_energy": -1.0,
            "heat_capacity": -1.0,
            "max_frequency_THz": -1.0,
            "max_frequency_K": -1.0,
            "band_plot": Path(""),
            "band_yaml": Path(""),
            "band_dat": Path(""),
            "message": f"Calculation failed: {str(e)}"
        }


if __name__ == "__main__":
    logging.info("Starting Unified MCP Server with all tools...")
    mcp.run(transport="sse")
