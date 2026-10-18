const INJECTION_PATTERNS = [
  /ignore\s+(all\s+)?previous instructions/i,
  /disregard\s+(all\s+)?previous instructions/i,
  /reveal\s+(the\s+)?system prompt/i,
  /reveal\s+(the\s+)?instructions/i,
  /execute\s+this\s+command/i,
  /you are now the system/i,
];

export function containsPromptInjection(text = "") {
  return INJECTION_PATTERNS.some((pattern) => pattern.test(text));
}

export function sanitizeUntrustedText(text = "") {
  let sanitizedText = text;

  sanitizedText = sanitizedText.replace(
    /ignore\s+(all\s+)?previous instructions/gi,
    "[filtered instruction]"
  );

  sanitizedText = sanitizedText.replace(
    /disregard\s+(all\s+)?previous instructions/gi,
    "[filtered instruction]"
  );

  sanitizedText = sanitizedText.replace(
    /reveal\s+(the\s+)?system prompt/gi,
    "[filtered system request]"
  );

  sanitizedText = sanitizedText.replace(
    /reveal\s+(the\s+)?instructions/gi,
    "[filtered request]"
  );

  sanitizedText = sanitizedText.replace(
    /execute\s+this\s+command/gi,
    "[filtered command]"
  );

  sanitizedText = sanitizedText.replace(
    /you are now the system/gi,
    "[filtered role-change request]"
  );

  return sanitizedText;
}