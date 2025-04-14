# How to Run This Awesome Project

- if ! command -v poetry &> /dev/null; then\n   # Check if Poetry available, if not install it
    - curl -sSL https://install.python-poetry.org | python3 -\n
    - export PATH=\"\$HOME/.local/bin:\$PATH\"\n
- fi\n


1. **Step into the Matrix**: Navigate to the project folder like a boss and activate the poetry virtual environment with:
    - `poetry shell`
    - (Cue the dramatic music)

2. **Summon the Dependencies**: Install all the dependencies and libraries that will make this project shine:
    - `poetry install --no-interaction --no-root`
    - (It's like magic, but better)

3. **Launch the Beast**: You're almost there! Run the following command to start the Dash server:
    - `poetry run python app.py`
    - (Feel the power at your fingertips)

4. **Witness the Magic**: Open your browser and go to [http://127.0.0.1:8050/](http://127.0.0.1:8050/) and behold the marvel you've just unleashed.
    - (Voila! 🎉)

Enjoy your journey, and may the code be with you!
