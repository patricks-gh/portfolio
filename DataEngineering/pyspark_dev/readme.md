# PySpark Demo - Development Environment

This repository contains a sample PySpark project. A great guide for setting up and running SQL queries directly on your CSV files **LOCALLY** with **zero architecture setup required**!

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
   - [Install Python](#install-python)
   - [Install Apache Spark](#install-apache-spark)
   - [Install Java](#install-java)
4. [Setting Up Environment Variables](#setting-up-environment-variables)
   - [Set JAVA_HOME](#set-java_home)
   - [Set SPARK_HOME](#set-spark_home)
5. [Running the Project](#running-the-project)

---

## Introduction

This repository provides a sample project demonstrating the power of **PySpark**. It allows you to run SQL queries directly on CSV files without needing any complex setup. Just install the prerequisites and you’re ready to go!

---

## Prerequisites

Before running this project, ensure you have the following installed on your machine:

- **Python** 3.6 or above
- **Apache Spark** (Local version)
- **Java** (JDK 17 or above)

---

## Setup Instructions

Follow these steps to set up the development environment.

### Install Python

1. Ensure you have Python 3.6 or above installed. You can download Python from [here](https://www.python.org/downloads/).
2. Install **PySpark** using pip:

   ```bash
   pip install pyspark
   ```

### Install Java

1. Install **Java JDK 17** or above. You can download it from the [AdoptOpenJDK website](https://adoptopenjdk.net/) or [Oracle's official download page](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html).
2. Verify the installation with:

   ```bash
   java -version
   ```

### Install PySpark

To install **PySpark**, use the following `pip` command:

```bash
python -m pip install pyspark
```

## Setting Up Environment Variables

To run PySpark, you need to configure the following environment variables:

### Set JAVA_HOME

#### For macOS/Linux:

1. Open your terminal.
2. Edit your profile configuration file (`~/.bash_profile`, `~/.bashrc`, `~/.zshrc`, etc.).
3. Add the following lines:

   ```bash
   export JAVA_HOME=$(/usr/libexec/java_home -v 17)
   export PATH=$JAVA_HOME/bin:$PATH
   ```
#### For Windows:

1. Open "Environment Variables" settings and add a new variable named JAVA_HOME with the path to your JDK installation.
2. Add %JAVA_HOME%\bin to your Path variable.

## Running the Project

Once the prerequisites are set up and the environment variables are configured, you can run the PySpark project.

### Clone the Repository

First, clone this repository to your local machine using Git:

```bash
git clone https://github.com/patricks-gh/portfolio/tree/main/DataEngineering/pyspark_dev.git
```

### Navigate to the Project Directory

After cloning, navigate into the project directory:

```bash
cd pyspark_dev/introduction
```

### Run the PySpark Script

```bash
python app.py > out.txt 2> err.txt
```

### View the Results stored in out.txt and err.txt

Output is gonna be saved in plain text to avoid overflowing your terminal with INFO.