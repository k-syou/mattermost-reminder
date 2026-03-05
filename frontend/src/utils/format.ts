export function formatDaysOfWeek(days: number[]): string {
  const dayNames = ['일', '월', '화', '수', '목', '금', '토']
  const sortedDays = [...days].sort((a, b) => a - b)
  return sortedDays.map(day => dayNames[day]).join(', ')
}

export function formatTime(time: string): string {
  return time
}
