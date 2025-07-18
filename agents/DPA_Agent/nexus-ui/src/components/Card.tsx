import React from 'react'
import { motion } from 'framer-motion'
import classNames from 'classnames'

interface CardProps {
  children: React.ReactNode
  className?: string
  hoverable?: boolean
  onClick?: () => void
}

const Card: React.FC<CardProps> = ({ 
  children, 
  className, 
  hoverable = false,
  onClick 
}) => {
  return (
    <motion.div
      whileHover={hoverable ? { y: -2 } : undefined}
      className={classNames(
        'card',
        {
          'cursor-pointer': onClick,
        },
        className
      )}
      onClick={onClick}
    >
      {children}
    </motion.div>
  )
}

export default Card