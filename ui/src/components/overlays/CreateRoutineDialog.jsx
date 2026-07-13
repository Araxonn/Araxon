import React, { useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../ui/dialog'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Plus, Trash2 } from 'lucide-react'

const CreateRoutineDialog = () => {
  const { createRoutineOpen, setCreateRoutineOpen } = useAppStore()
  const { sendCommand } = useWebSocket()

  const [name, setName] = useState('')
  const [steps, setSteps] = useState([
    { text: '', type: 'open_app' },
  ])

  const handleAddStep = () => {
    setSteps([...steps, { text: '', type: 'open_app' }])
  }

  const handleRemoveStep = (idx) => {
    setSteps(steps.filter((_, i) => i !== idx))
  }

  const handleStepChange = (idx, field, value) => {
    const newSteps = [...steps]
    newSteps[idx] = { ...newSteps[idx], [field]: value }
    setSteps(newSteps)
  }

  const handleCreate = () => {
    if (name.trim() && steps.some((s) => s.text.trim())) {
      const routineData = {
        name,
        steps: steps.map((s) => ({ ...s })),
      }
      sendCommand(`create routine: ${JSON.stringify(routineData)}`)
      setName('')
      setSteps([{ text: '', type: 'open_app' }])
      setCreateRoutineOpen(false)
    }
  }

  const stepTypes = [
    'open_app',
    'open_website',
    'run_command',
    'speak',
  ]

  return (
    <Dialog open={createRoutineOpen} onOpenChange={setCreateRoutineOpen}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Routine</DialogTitle>
          <DialogDescription>
            Define a sequence of actions to automate
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Routine Name */}
          <div>
            <label className="text-xs font-semibold text-arx-text mb-1 block">
              Routine Name
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Deploy Setup"
              className="h-8 text-xs"
            />
          </div>

          {/* Steps */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-arx-text">Steps</label>
            <div className="max-h-48 overflow-y-auto space-y-2">
              {steps.map((step, idx) => (
                <div key={idx} className="flex gap-2 items-end">
                  <div className="flex-1 min-w-0 space-y-1">
                    <select
                      value={step.type}
                      onChange={(e) =>
                        handleStepChange(idx, 'type', e.target.value)
                      }
                      className="w-full h-7 text-xs bg-arx-input border border-arx-border rounded px-2 text-arx-text"
                    >
                      {stepTypes.map((type) => (
                        <option key={type} value={type}>
                          {type.replace('_', ' ')}
                        </option>
                      ))}
                    </select>
                    <Input
                      value={step.text}
                      onChange={(e) =>
                        handleStepChange(idx, 'text', e.target.value)
                      }
                      placeholder={`${step.type} name or command...`}
                      className="h-7 text-xs"
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-arx-red"
                    onClick={() => handleRemoveStep(idx)}
                  >
                    <Trash2 size={12} />
                  </Button>
                </div>
              ))}
            </div>

            <Button
              variant="outline"
              size="sm"
              className="w-full h-7 text-xs"
              onClick={handleAddStep}
            >
              <Plus size={12} className="mr-1" />
              Add Step
            </Button>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setCreateRoutineOpen(false)}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={!name.trim() || !steps.some((s) => s.text.trim())}
          >
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default CreateRoutineDialog
