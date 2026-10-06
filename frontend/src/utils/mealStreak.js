function localDateKey(date) {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

/**
 * Return the active meal logging streak in local calendar days.
 * The streak may end today or yesterday, so it remains active until the user
 * misses a full calendar day.
 */
export function calculateCurrentMealStreak(meals = [], now = new Date()) {
  const loggedDates = new Set();

  meals.forEach((meal) => {
    if (!meal?.logged_at) return;
    const loggedAt = new Date(meal.logged_at);
    if (!Number.isNaN(loggedAt.getTime())) {
      loggedDates.add(localDateKey(loggedAt));
    }
  });

  const streakDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  if (!loggedDates.has(localDateKey(streakDate))) {
    streakDate.setDate(streakDate.getDate() - 1);
  }

  let streakDays = 0;
  while (loggedDates.has(localDateKey(streakDate))) {
    streakDays += 1;
    streakDate.setDate(streakDate.getDate() - 1);
  }

  return streakDays;
}
