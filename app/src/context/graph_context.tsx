import * as React from "react"
import { GraphType, SetGraphType } from "../types"

// Default value - when context provider is not available.
export const GraphContext = React.createContext<GraphType | undefined>(undefined)
export const SetGraphContext = React.createContext<SetGraphType>(() => undefined)

export const useGraph = () => React.useContext(GraphContext)
export const useSetGraph = () => React.useContext(SetGraphContext)

export function AppContext(props: any) {
  const [graph, setGraph] = React.useState<GraphType>();

  return (
    <GraphContext.Provider value={graph}>
        <SetGraphContext.Provider value={setGraph}>{props.children}</SetGraphContext.Provider>
    </GraphContext.Provider>
  )
}
