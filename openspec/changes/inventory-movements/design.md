# Design: inventory-movements

## Architecture & Data Flow

1. **Table: `stock_movement`**
   - Fields:
     - `id` (int, primary key)
     - `product_id` (int, foreign key reference to product)
     - `movement_type` (text: "entry", "exit", "adjustment")
     - `quantity` (int, positive value representing units added or removed)
     - `previous_stock` (int)
     - `new_stock` (int)
     - `reason` (text, required justification)
     - `user_id` (int, optional/nullable or linked to user)
     - `created_at` (timestamp, now)

2. **Endpoint: `POST /api:smart_vision/stock_entry`**
   - Inputs: `product_id` (int), `quantity` (int > 0), `reason` (text), `user_id` (int, optional).
   - Logic:
     1. Validate `quantity > 0`.
     2. Fetch product record.
     3. Calculate `previous_stock = product.current_stock` and `new_stock = previous_stock + quantity`.
     4. Insert record into `stock_movement` table (Audit record created FIRST).
     5. Update product `current_stock` to `new_stock`.
     6. Return movement record and updated product.

3. **Endpoint: `POST /api:smart_vision/stock_exit`**
   - Inputs: `product_id` (int), `quantity` (int > 0), `reason` (text), `user_id` (int, optional).
   - Logic:
     1. Validate `quantity > 0`.
     2. Fetch product record.
     3. Calculate `previous_stock = product.current_stock` and `new_stock = previous_stock - quantity`.
     4. Precondition check: `new_stock >= 0` (or require explicit adjustment reason/approval if negative allowed). Per AGENTS.md 1.2: "Se uma saída tentaria deixar o saldo negativo, deve rejeitar a operação".
     5. Insert record into `stock_movement` table.
     6. Update product `current_stock` to `new_stock`.
     7. Return movement record and updated product.

