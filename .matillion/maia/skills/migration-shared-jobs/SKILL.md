## Shared jobs

There are some additional factors to consider when upgrading a Matillion ETL shared job to a Data Productivity Cloud shared pipeline. To correctly upgrade shared jobs, use the process given below.

Before doing this, ensure that you fully understand the concepts and use of both shared jobs in Matillion ETL and shared pipelines in the Data Productivity Cloud.

Best practice for shared pipelines is to create them in their own dedicated project that is separate from the projects that consume them. These instructions assume you will be doing that.

### Upgrade path

1. In Matillion ETL, **unpack** the shared jobs you want to export.  

   > **Note**  
   > If you have the original source of the shared jobs, you can skip this step and export the source instead.

2. Export the unpacked jobs, as described in *Export from Matillion ETL*.

3. In the Data Productivity Cloud, import the shared jobs, as described in *Import to the Data Productivity Cloud*. Ensure that you are importing into the project you are using to hold your shared pipelines.

4. Refactor, test, and amend these pipelines as needed to ensure they perform the expected function in the Data Productivity Cloud.

5. Share the pipelines, as described in *Sharing a pipeline*.

6. In Matillion ETL, **export** the jobs that use the shared jobs.

7. In the Data Productivity Cloud, **import** the exported jobs. These will become your *consuming pipelines* in the Data Productivity Cloud.

8. Create a *mapping* to resolve any issues in the import that require refactoring. Read *Shared job mappings* to learn how to do this.

9. Refactor and test the imported pipeline to ensure it functions as expected and correctly calls the shared pipelines it needs.

> **Note**  
> Shared Jobs will be shown as **Unknown** components in the `component_details.csv` file.

### Shared job mappings

The mapping feature gives you a tool to resolve issues in migrating shared jobs from Matillion ETL to Data Productivity Cloud shared pipelines.

When following the import process, shared job components in Matillion ETL won't have direct equivalents in the Data Productivity Cloud, and will result in a **Manual refactor** status for the imported pipeline. A pipeline with this status won't validate or run until you edit the pipeline to replace the "unknown" components with suitably configured Data Productivity Cloud equivalents.

Mapping provides a mechanism for you to tell the Data Productivity Cloud how to perform these replacements automatically, across all your imported pipelines. You may still choose to manually edit the pipeline, but mapping gives you an alternative process that avoids the need to click through the configuration of all the pipelines and component properties via the canvas UI.

### Mapping process

After importing, if the *Importing files* panel shows pipelines that require **Manual refactor**, follow this process:

1. Click **Add mapping** in the **Manual refactor** section of the panel.

2. Enter the mapping information in the **Add mappings for imported jobs** dialog, in JSON format as described in *Structure of the mapping*, below.  
   The dialog will autocomplete necessary syntax (such as `}`, `]`) to ensure the JSON is well-formed.

   > **Note**  
   > There is no mechanism for saving the mapping. If it's a mapping you intend to reuse (for example, if you use the same shared job in many different jobs that you intend t


