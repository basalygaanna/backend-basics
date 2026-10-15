# Правила API

- URL в kebab-case, JSON в snake_case
- tags Books/Readers/Loans
- post, patch, put, delete только с авторизацией Bearer JWT
- Ресурсы — существительные во множественном числе
- id в path, фильтры в query
- Даты — ISO 8601 (format: date-time)
- Ошибки — единый ErrorResponse
- Фильтры, сортировка, пагинация на коллекциях
- Request/response — раздельные схемы.
- additionalProperties: false в request-схемах.
- Idempotency-Key на POST /loans: полный replay ответа, конфликт другого тела,
конкурентные повторы и срок хранения 24 часа;
- Возврат: POST /loans/{id}/return, не DELETE
- Версия в servers (/v1).
- Помечать устаревшие поля через deprecated: true