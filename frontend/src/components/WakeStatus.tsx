interface WakeStatusProps {
  awake: boolean
  message: string
}

export const WakeStatus: React.FC<WakeStatusProps> = ({ awake, message }) => {
  return (
    <div className="fixed bottom-4 left-4 z-50 px-3 py-1.5 rounded-full text-xs font-medium border">
      {awake ? (
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-green-700">{message}</span>
        </div>
      ) : (
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse"></span>
          <span className="text-amber-700">{message}</span>
        </div>
      )}
    </div>
  )
}
