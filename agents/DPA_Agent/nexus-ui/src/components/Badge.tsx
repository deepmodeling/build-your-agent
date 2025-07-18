import React from 'react'
import classNames from 'classnames'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'success' | 'warning' | 'error' | 'info'
  className?: string
}

const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'info', 
  className 
}) => {
  const variantClasses = {
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
    info: 'badge-info',
  }

  return (
    <span className={classNames('badge', variantClasses[variant], className)}>
      {children}
    </span>
  )
}

export default Badge