import * as React from "react"
import { cn } from "@/lib/utils"

const Input = React.forwardRef(({ className, type, ...props }, ref) => (
  <input
    type={type}
    className={cn(
      "flex h-9 w-full rounded-md border border-arx-border bg-arx-input px-3 py-1 text-sm text-arx-text placeholder:text-arx-muted transition-colors focus-visible:outline-none focus-visible:border-arx-blue disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    ref={ref}
    {...props}
  />
))
Input.displayName = "Input"

export { Input }
