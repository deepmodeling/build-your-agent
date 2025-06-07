"""
XYZ Utilities Module

Provides functionality for processing XYZ format and 3D structure data.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import requests

# Try to import RDKit, use None if not available
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    logging.warning("Warning: RDKit is not installed or cannot be loaded. 3D structure generation will be limited.")
    RDKIT_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Cache directory
CACHE_DIR = Path.home() / '.pubchem-mcp' / 'cache'

# Ensure cache directory exists
try:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    logger.error(f"Unable to create cache directory: {e}")


class Atom:
    """Atom class, represents an atom in 3D space"""

    def __init__(self, symbol: str, x: float, y: float, z: float):
        self.symbol = symbol
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f"{self.symbol} {self.x:.6f} {self.y:.6f} {self.z:.6f}"


class XYZData:
    """XYZ data class, represents a molecule's 3D structure"""

    def __init__(self, atom_count: int, info: str, atoms: List[Atom]):
        self.atom_count = atom_count
        self.info = info
        self.atoms = atoms

    def to_string(self) -> str:
        """Convert XYZ data to XYZ format string"""
        result = f"{self.atom_count}\n{self.info}\n"
        for atom in self.atoms:
            # Ensure element symbol is not empty, use default "C" if empty
            symbol = atom.symbol if atom.symbol and atom.symbol.strip() and atom.symbol != "0" else "C"
            result += f"{symbol} {atom.x:.6f} {atom.y:.6f} {atom.z:.6f}\n"
        return result


def download_sdf_from_pubchem(cid: str) -> Optional[str]:
    """Download SDF format 3D structure from PubChem"""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF/?record_type=3d&response_type=display&display_type=sdf"
    logger.info(f"Downloading SDF from: {url}")
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200 and response.text:
            logger.info(f"Successfully downloaded SDF for CID: {cid} (Length: {len(response.text)})")
            return response.text
        else:
            logger.error(f"Failed to download SDF, CID: {cid}. Status code: {response.status_code}, Content empty: {not response.text}")
            return None
    except Exception as e:
        logger.error(f"Error downloading SDF, CID: {cid}. Error: {e}", exc_info=True)
        return None


def generate_3d_from_smiles(smiles: str) -> Optional[Any]:
    """Generate 3D structure from SMILES using RDKit"""
    if not RDKIT_AVAILABLE:
        logger.error("RDKit not installed, cannot generate 3D structure from SMILES")
        return None
    logger.info(f"Attempting to generate 3D from SMILES: {smiles}")
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            logger.warning("RDKit MolFromSmiles returned None.")
            return None
        mol_with_h = Chem.AddHs(mol)
        embed_result = AllChem.EmbedMolecule(mol_with_h, randomSeed=42)
        if embed_result < 0: # EmbedMolecule returns -1 on failure
             logger.warning("RDKit EmbedMolecule failed.")
             return None
        optimize_result = AllChem.MMFFOptimizeMolecule(mol_with_h)
        if optimize_result != 0: # MMFFOptimizeMolecule returns 0 on success, 1 on failure
            logger.warning("RDKit MMFFOptimizeMolecule failed.")
            # Continue anyway, maybe the unoptimized structure is usable
        logger.info("Successfully generated 3D structure from SMILES.")
        return mol_with_h
    except Exception as e:
        logger.error(f"Error generating 3D structure from SMILES: {e}", exc_info=True)
        return None


def sdf_to_mol(sdf_content: str) -> Optional[Any]:
    """Create RDKit molecule object from SDF text content"""
    if not RDKIT_AVAILABLE:
        logger.error("RDKit not installed, cannot create molecule object from SDF")
        return None
    if not sdf_content:
        logger.warning("sdf_to_mol received empty SDF content.")
        return None
    logger.info("Attempting to convert SDF block to RDKit Mol...")
    try:
        mol = Chem.MolFromMolBlock(sdf_content, removeHs=False)
        if mol is None:
            logger.warning("RDKit MolFromMolBlock returned None.")
            return None
        # Optional: Check/add hydrogens if needed, though 3D SDF usually has them
        # has_hydrogens = any(atom.GetAtomicNum() == 1 for atom in mol.GetAtoms())
        # if not has_hydrogens:
        #     logger.info("Adding hydrogens and embedding/optimizing...")
        #     mol = Chem.AddHs(mol)
        #     AllChem.EmbedMolecule(mol, randomSeed=42)
        #     AllChem.MMFFOptimizeMolecule(mol)
        logger.info("Successfully created RDKit Mol from SDF.")
        return mol
    except Exception as e:
        logger.error(f"Error in sdf_to_mol: Failed converting SDF to RDKit Mol object. SDF start: '{sdf_content[:100]}...'. Error: {e}", exc_info=True)
        return None


def parse_sdf(sdf_content: str) -> Optional[List[Atom]]:
    """Simple SDF parser, does not depend on RDKit (Use as fallback only)"""
    logger.info("Attempting to parse SDF with custom parser...")
    if not sdf_content:
        logger.warning("Custom parse_sdf received empty SDF content.")
        return None
    try:
        lines = sdf_content.strip().split('\n')
        if len(lines) < 4:
            logger.warning("Custom parser: SDF has less than 4 lines.")
            return None

        counts_line = lines[3].strip()
        atom_count = int(counts_line[:3].strip())
        if atom_count <= 0:
            logger.warning(f"Custom parser: Invalid atom count ({atom_count}).")
            return None

        atoms = []
        for i in range(atom_count):
            line_index = 4 + i
            if line_index >= len(lines):
                logger.warning(f"Custom parser: Reached end of file unexpectedly at atom {i+1}/{atom_count}.")
                break
            line = lines[line_index]
            try:
                x = float(line[0:10].strip())
                y = float(line[10:20].strip())
                z = float(line[20:30].strip())
                symbol = line[31:34].strip()
                if not symbol or not symbol.isalpha(): # Basic check for element symbol
                    # Fallback regex attempt if fixed columns fail
                    match = re.match(r'\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+([A-Za-z]{1,2})', line)
                    if match:
                        symbol = match.group(4)
                    else:
                        logger.warning(f"Custom parser: Could not parse symbol from line: {line.strip()}")
                        symbol = "X" # Use placeholder if symbol parsing fails
                atoms.append(Atom(symbol, x, y, z))
            except (ValueError, IndexError) as parse_err:
                logger.warning(f"Custom parser: Error parsing atom line {line_index+1}: '{line.strip()}'. Error: {parse_err}")
                continue # Skip problematic line

        if not atoms:
            logger.warning("Custom parser: No atoms could be parsed.")
            return None

        logger.info(f"Custom parser successfully parsed {len(atoms)} atoms.")
        return atoms
    except Exception as e:
        logger.error(f"Error in custom parse_sdf: {e}", exc_info=True)
        return None


def mol_to_xyz(mol: Any, compound_info: Dict[str, str]) -> Optional[str]:
    """Convert RDKit molecule object to XYZ format string"""
    if not RDKIT_AVAILABLE:
        logger.error("RDKit not installed, cannot convert to XYZ format")
        return None
    if mol is None:
        logger.warning("mol_to_xyz received None Mol object.")
        return None
    logger.info("Attempting to convert RDKit Mol to XYZ string...")
    try:
        conf = mol.GetConformer() # Assumes conformer exists
        if not conf:
             logger.error("RDKit Mol object has no conformer.")
             return None

        xyz_content = f"{mol.GetNumAtoms()}\n"
        info_parts = [f"{key}={value}" for key, value in compound_info.items() if value]
        xyz_content += " ".join(info_parts) + "\n"

        for i in range(mol.GetNumAtoms()):
            atom = mol.GetAtomWithIdx(i)
            pos = conf.GetAtomPosition(i)
            xyz_content += f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n"

        logger.info("Successfully converted RDKit Mol to XYZ string.")
        return xyz_content
    except Exception as e:
        logger.error(f"Error in mol_to_xyz: Failed converting RDKit Mol object to XYZ string. Error: {e}", exc_info=True)
        return None


def get_xyz_structure(sdf_content: Optional[str], cid: str, smiles: str, compound_info: Dict[str, str]) -> Optional[str]:
    """
    Get XYZ format 3D structure of a compound.
    Prioritizes converting provided sdf_content, falls back to downloading/generating if needed.
    """
    logger.info(f"Getting XYZ structure: cid={cid}, sdf_provided={sdf_content is not None}")
    xyz_string = None
    cache_file = CACHE_DIR / f"{cid}.xyz"

    # --- Primary Path: Process provided SDF content ---
    if sdf_content:
        logger.info("Processing provided SDF content...")
        if RDKIT_AVAILABLE:
            mol = sdf_to_mol(sdf_content)
            if mol:
                xyz_string = mol_to_xyz(mol, compound_info)
        # If RDKit failed or not available, try custom parser
        if not xyz_string:
            logger.info("RDKit failed or unavailable for provided SDF, trying custom parser...")
            atoms = parse_sdf(sdf_content)
            if atoms:
                info_line = ' '.join(f"{k}={v}" for k, v in compound_info.items() if v)
                xyz_data = XYZData(len(atoms), info_line, atoms)
                xyz_string = xyz_data.to_string()
                logger.info("Custom parser generated XYZ from provided SDF.")

        if xyz_string:
            logger.info("Successfully generated XYZ from provided SDF.")
            # Save to cache even if SDF was provided externally
            try:
                cache_file.write_text(xyz_string, encoding='utf-8')
                logger.info(f"Saved XYZ (from provided SDF) to cache: {cache_file}")
            except Exception as e:
                logger.error(f"Error writing cache file {cache_file}: {e}")
            return xyz_string
        else:
            logger.warning("Failed to generate XYZ from provided SDF content.")
            # Continue to fallbacks if processing provided SDF fails

    # --- Fallback Path: If SDF not provided or processing failed ---
    logger.info("Attempting fallback methods (cache check, download, SMILES generation)...")

    # Fallback 1: Check cache
    if cache_file.exists():
        try:
            logger.info(f"Reading XYZ structure from cache: {cache_file}")
            return cache_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading cache file {cache_file}: {e}")

    # Fallback 2: Download SDF and process it (if not provided initially)
    if not sdf_content: # Only download if SDF wasn't provided
        downloaded_sdf = download_sdf_from_pubchem(cid)
        if downloaded_sdf:
            logger.info("Processing downloaded SDF...")
            if RDKIT_AVAILABLE:
                mol = sdf_to_mol(downloaded_sdf)
                if mol:
                    xyz_string = mol_to_xyz(mol, compound_info)
            # If RDKit failed or not available, try custom parser
            if not xyz_string:
                logger.info("RDKit failed or unavailable for downloaded SDF, trying custom parser...")
                atoms = parse_sdf(downloaded_sdf)
                if atoms:
                    info_line = ' '.join(f"{k}={v}" for k, v in compound_info.items() if v)
                    xyz_data = XYZData(len(atoms), info_line, atoms)
                    xyz_string = xyz_data.to_string()
                    logger.info("Custom parser generated XYZ from downloaded SDF.")

            if xyz_string:
                 logger.info("Successfully generated XYZ from downloaded SDF.")
                 # Save to cache
                 try:
                     cache_file.write_text(xyz_string, encoding='utf-8')
                     logger.info(f"Saved XYZ (from downloaded SDF) to cache: {cache_file}")
                 except Exception as e:
                     logger.error(f"Error writing cache file {cache_file}: {e}")
                 return xyz_string
            else:
                 logger.warning("Failed to generate XYZ from downloaded SDF.")
        else:
            logger.warning("Failed to download SDF as fallback.")

    # Fallback 3: Generate from SMILES using RDKit (if all SDF methods failed)
    if RDKIT_AVAILABLE and smiles:
        logger.info(f"Attempting to generate 3D structure from SMILES as final fallback: {smiles}")
        mol = generate_3d_from_smiles(smiles)
        if mol:
            xyz_string = mol_to_xyz(mol, compound_info)
            if xyz_string:
                logger.info("Successfully generated XYZ from SMILES.")
                # Save to cache
                try:
                    cache_file.write_text(xyz_string, encoding='utf-8')
                    logger.info(f"Saved XYZ (from SMILES) to cache: {cache_file}")
                except Exception as e:
                    logger.error(f"Error writing cache file {cache_file}: {e}")
                return xyz_string
            else:
                logger.warning("mol_to_xyz returned None (from SMILES).")
        else:
            logger.warning("generate_3d_from_smiles returned None.")

    logger.error(f"All methods failed to generate XYZ structure for CID {cid}.")
    return None # All methods failed


# Periodic table - atomic number mapping (Unchanged)
ELEMENT_NUMBERS = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
    'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20,
    'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30,
    'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40,
    'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60,
    'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70,
    'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80,
    'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90,
    'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100
}


def get_atomic_number(symbol: str) -> int:
    """Get atomic number for an element symbol"""
    return ELEMENT_NUMBERS.get(symbol, 0)
