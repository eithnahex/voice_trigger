# INSTALL

> !!! WARN !!!
> <br>Temporary support for Windows OS only<br><br>

<br>

- recommends:
    - use `venv` or `virtualenv`
- install `python >= 3.10.5`
- install `pytorch`: 
    ```python
    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
    ```
- install other deps:
    ```python
    pip install -r requirements.txt
    ```
- you are `beautiful`! ;)

## Windows OS

- install [Virtual Audio Cable](https://vb-audio.com/Cable/)


## Discord

- in voice settings set `input device` to "CABLE Output (VB-Audio Virtual Cable)"

# RUN

```python
python main.py
```