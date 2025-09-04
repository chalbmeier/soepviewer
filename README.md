# SOEPViewer

A desktop application to make working with [SOEP](https://www.diw.de/en/diw_01.c.615551.en/research_infrastructure__socio-economic_panel__soep.html) metadata easier.  

## Requirements

- Windows 10/11
- Python 3.11+
- SOEP documentation metadata

## Description

The [SOEP](https://www.diw.de/en/diw_01.c.615551.en/research_infrastructure__socio-economic_panel__soep.html) is a large German panel survey that specifies the content of its data and questionnaires in the [SOEP metadatabase](https://git.soep.de/kwenzig/publicecoredoku). The database consists of several hundred CSV files that contain survey questions and answers, datasets and variable names, as well as mappings between survey questions and variables. The files are often viewed or edited individually in spreadsheet software, which makes it hard to see how they relate. For example, tracing the connection between a specific survey question and its variables typically requires opening two to four CSV files—often twice as many when comparing questions across survey waves.

**SOEPViewer** is a prototype application that makes the handling of the CSV-based database easier. On startup, it automatically builds links between questions, answers, datasets, and variables and presents them in a user-friendly interface. For each question, it also lists related questions to support comparisons across survey waves and the versioning of variable names. In this way, SOEPViewer simplifies working with SOEP metadata.

<video controls width="400" src="https://github.com/user-attachments/assets/f0be631a-50a8-49ff-bfa5-dbb91a2b706b">
</video>

## Installation

```console
pip install "soepviewer@git+https://github.com/chalbmeier/soepviewer.git"
```

Get the SOEP documentation metadata:
```console
git clone https://git.soep.de/kwenzig/publicecoredoku.git
```

## Usage
Run the app from a terminal:

```console
soepviewer
```

On first launch, the app displays the path to the user configuration file. Edit that file to set the paths to 
the SOEP documentation metadata, and the specific questionnaires you want to work with. Restart the app after saving the configuration.

## Project status

This project is currently unmaintained. Feel free to adapt it to your needs.

## Development

Clone and run from source:
```console
git clone https://github.com/chalbmeier/soepviewer.git
cd soepviewer
python -m soepviewer
```
