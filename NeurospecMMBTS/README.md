# NeurospecMMBTS

This repository contains Python functions to use the [MMBT-S Trigger Box](https://www.neurospec.com/products/mmbt-s) by **NEUROSPEC** to connect and send event triggers to an EEG system. The Trigger Box serves as an USB-to-parallel port adapter, allowing computers without a physical parallel port to send triggers via serial port. The Trigger Box appears as a serial COM port (installing the corresponding driver may be required).

<br>

## Workflow to use the MMBT-S Trigger Box

1. Define port object (once in the beginning of the experiment):
```python
mmbts = MMBTS()
```

<br>

2. Open port to MMBT-S (once in the beginning of the experiment):
```python
mmbts.open_port("COM5")                     # for running the experiment
mmbts.open_port("COM5", debugging=True)     # with predefined debugging mode
```

<br>

3. Send triggers to EEG system (during the experiment):
```python
mmbts.send_trigger(10)
```

<br>

4. Close port to MMBT-S (once at the end of the experiment):
```python
mmbts.close_port()
```

<br>

**Additionally**, you can get a list of availablee ports by using:
```python
MMBTS.show_ports()
```

<br>

## Examples

**Demo Experiment**
```python
experiment_demo.py
```
- Demonstrates how to use the MMBT-S Trigger Box to send event triggers during an experiment. 

<br>

**Extraction Notebook** 
```python
extraction_demo.ipynb
```
- Demonstrates how to extract trigger events from [BioSemi](https://www.biosemi.com/index.htm) `BDF files` using [MNE-Python](https://mne.tools/stable/index.html) and aggregate them into a trial-level dataset.

<br>

**Example Data**
```python
NeurospecMMBTS/
│
└── example_data/
    ├── testdata_1024Hz_09112026.bdf
    ├── testdata_2048Hz_09112026.bdf
    └── testdata_512Hz_09112026.bdf
```
The folder `example_data` contains three data files recorded using the demo experiment at different sampling rates (512 Hz, 1024 Hz, and 2048 Hz).

<br>

## Requirements

- [Python (3.8+)](https://www.python.org/downloads/)
- [pySerial (3.5+)](https://pypi.org/project/pyserial/)

<br>

## References

Corresponding **MATLAB** functions for the MMBT-S Trigger Box can be found on the **GitHub repository** from **Dr. Niko Busch**: <br>
https://github.com/nabusch/NeurospecTriggerBox

<br>

Details about using **serial port** in Python can be found on the documentation website for **pySerial**: <br>
https://pyserial.readthedocs.io/en/latest/

<br>

A **video series** on using the MMBT-S Trigger Box by **Neurospec** is available on **YouTube**: <br>
https://www.youtube.com/playlist?list=PLlqnpgURTieauXe2OMGoQrt98rZuPfOJJ

<br>

Any **further information** about the MMBT-S Trigger Box can be found on the **NEUROSPEC** website: <br>
https://www.neurospec.com/products/mmbt-s

<br>

Information on the **BDF file format** can be found on the **BioSemi** website: <br>
https://www.biosemi.com/faq/file_format.htm

<br>

