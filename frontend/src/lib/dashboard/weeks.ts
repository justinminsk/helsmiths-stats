const monthIndexByToken: Record<string, number> = {
  jan: 1,
  january: 1,
  feb: 2,
  february: 2,
  mar: 3,
  march: 3,
  apr: 4,
  april: 4,
  may: 5,
  jun: 6,
  june: 6,
  jul: 7,
  july: 7,
  aug: 8,
  august: 8,
  sep: 9,
  sept: 9,
  september: 9,
  oct: 10,
  october: 10,
  nov: 11,
  november: 11,
  dec: 12,
  december: 12,
};

export type ParsedWeekLabel = {
  identity: string;
  sortKey: number;
};

export function parseWeekLabel(label: string) {
  const match = label.trim().match(/^([A-Za-z]+)\s+(\d{1,2})-(\d{1,2})$/);
  if (!match) {
    return null;
  }

  const [, rawMonth, rawStartDay, rawEndDay] = match;
  const monthIndex = monthIndexByToken[rawMonth.toLowerCase()];
  if (!monthIndex) {
    return null;
  }

  const startDay = Number(rawStartDay);
  const endDay = Number(rawEndDay);

  return {
    identity: `${monthIndex}-${startDay}-${endDay}`,
    sortKey: monthIndex * 100 + startDay,
  } satisfies ParsedWeekLabel;
}

export function compareWeekLabels(leftLabel?: string, rightLabel?: string) {
  const left = leftLabel?.trim() ?? '';
  const right = rightLabel?.trim() ?? '';

  if (!left && !right) {
    return 0;
  }
  if (!left) {
    return 1;
  }
  if (!right) {
    return -1;
  }

  const leftParsed = parseWeekLabel(left);
  const rightParsed = parseWeekLabel(right);

  if (leftParsed && rightParsed && leftParsed.sortKey !== rightParsed.sortKey) {
    return leftParsed.sortKey - rightParsed.sortKey;
  }
  if (leftParsed && !rightParsed) {
    return -1;
  }
  if (!leftParsed && rightParsed) {
    return 1;
  }

  return left.localeCompare(right);
}

export function getWeekIdentity(label?: string) {
  if (!label) {
    return '';
  }

  return parseWeekLabel(label)?.identity ?? label.trim().toLowerCase();
}