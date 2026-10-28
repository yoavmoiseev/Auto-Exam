# TODO: Duplicate Question Text

## Problem

Exam answers are currently keyed by question text in the student submission flow. When an exam contains the same question text twice, the second answer overwrites the first in the answer map. The exam can then be reported as incomplete even when the student answered every displayed question. The same text-keyed design can also collapse answers during grading and in saved result reports.

## Partial fix now in place

- Exam validation detects repeated question text (ignoring case, repeated whitespace, Unicode compatibility differences, and bidirectional formatting marks).
- The Exam Data view shows the duplicate error with both question numbers and headings using its existing validation-error display.
- The server refuses to start an exam containing duplicate question text through both exam-start routes.

This is an interim guard. It prevents the known failure by requiring the teacher to remove or reword a duplicate before starting the exam. It does not support repeated question text as a valid exam design.

## Remaining TODOs

- Replace question-text keys with stable, unique question IDs from parsing through the student form, submission API, grading, session storage, HTML results, and exported result files.
- Grade answers by question ID and each question's own correct answer, so repeated wording cannot merge answers or distort the score.
- Preserve each submitted answer by question ID when rendering and saving results.
- Decide whether identical question text should be permitted after ID-based handling exists. If permitted, make duplicate detection informational; otherwise retain it as a blocking validation error.
- Add regression coverage for duplicate question text, duplicate questions with different correct answers, and ordinary exams with no duplicates.
- Review the parser rule that treats any line beginning with a number and a period as a new question; numbered instructions or answer content may be misclassified.

## Scope of this patch

Only duplicate detection and the server-side launch block are implemented here. The end-to-end question-ID redesign and the other TODOs above remain unresolved.
