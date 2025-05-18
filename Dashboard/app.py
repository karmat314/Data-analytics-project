# Directory structure (create these files accordingly):
# modular_dash_app/
# ├── app.py
# ├── layout.py
# ├── callbacks.py
# └── sections/
#     ├── __init__.py
#     └── economic.py

# === app.py ===
from dash import Dash
from layout import create_layout
from callbacks import register_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Russia vs Ukraine Dashboard"
app.layout = create_layout(app)

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)







