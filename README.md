## Setup

1. **Install dependencies using [uv]:**

   ```powershell
   uv sync
   ```

2. **Install `googletrans` manually (required for back translation):**
   ```powershell
   uv pip install googletrans==4.0.2
   ```
   > **Note:** If you skip this step, you may encounter  
   > `ModuleNotFoundError: No module named 'googletrans'`
