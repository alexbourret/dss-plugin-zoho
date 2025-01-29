# Zoho Platform Plugin for Dataiku

## Overview

This plugin enables seamless integration between Zoho WorkDrive and Zoho CRM with Dataiku DSS. You can use this plugin to read from and write data to Zoho WorkDrive, as well as read 
access Zoho CRM data. This allows you to leverage the capabilities of both platforms within your data science projects.

## Features

- **Read Data from Zoho WorkDrive**: Import documents and files stored in Zoho WorkDrive into Dataiku datasets.
- **Write Data to Zoho WorkDrive**: Export Dataiku datasets as documents or files back to Zoho WorkDrive.
- **Read Data from Zoho CRM**: Access and import data from Zoho CRM modules directly into Dataiku datasets.
- **Authentication**: Securely connect to Zoho services using OAuth 2.0 for authentication.

## Requirements

- Dataiku DSS version 6.0 or later
- Access to a Zoho WorkDrive account with read/write permissions
- Access to a Zoho CRM account with read permissions

## Installation

1. Download the plugin from the [Zoho Platform Plugin Repository](#).
2. In Dataiku DSS, go to `Settings` > `Plugins`.
3. Click on `Add a new plugin` and upload the downloaded plugin file.
4. Restart your Dataiku server if prompted.

## Configuration

### Setting Up OAuth 2.0 for Zoho WorkDrive and CRM

1. Go to the [Zoho Developer Console](https://www.zoho.com/developer/apps) and create two separate client applications: one for WorkDrive and one for CRM.
2. Set the `Redirect URI` for both applications to `http://<your_dataiku_instance><:your_data_instance_port>/dip/api/oauth2-callback`.
3. Note down the `Client ID` and `Client Secret` for each application.

### Plugin Configuration

1. In Dataiku, navigate to `Settings` > `Plugins` > `Zoho Platform`.
2. Enter your `WorkDrive Client ID`, `WorkDrive Client Secret`, and `CRM Client ID`, `CRM Client Secret`, and `Redirect URI` for both services.
3. Click on `Authenticate` to initiate the OAuth 2.0 flow for each service.
4. Follow the instructions to authorize access and obtain access tokens.

## Usage

### Reading Data from Zoho WorkDrive

1. Create a new recipe or script in your project.
2. Add the "Zoho WorkDrive Reader" action from the plugin actions list.
3. Configure the reader with the path to the document or file you wish to read.
4. Execute the recipe to import data into a Dataiku dataset.

### Writing Data to Zoho WorkDrive

1. Create a new recipe or script in your project.
2. Add the "Zoho WorkDrive Writer" action from the plugin actions list.
3. Configure the writer with the target path and file name on Zoho WorkDrive.
4. Execute the recipe to export data from a Dataiku dataset.

### Reading Data from Zoho CRM

1. Create a new recipe or script in your project.
2. Add the "Zoho CRM Reader" action from the plugin actions list.
3. Select the CRM module and specify fields you wish to import.
4. Execute the recipe to pull data into a Dataiku dataset.

## Troubleshooting

- **Authentication Issues**: Ensure that `Client IDs`, `Client Secrets`, and `Redirect URIs` are correctly configured for both Zoho WorkDrive and CRM in both the Zoho Developer Console 
and Dataiku plugin settings.
- **File/Module Access Errors**: Verify that specified paths or modules exist and that you have the necessary permissions to access them.

## License

This plugin is distributed under the Apache License version 2.0
