# Extract SQL Queries from SSIS PACKAGE (.DTSX) FILES

This Python script scrapes SQL queries from Data Flow and Execute SQL tasks inside of .dtsx files and writes them to SQL files in 'sql_scripts' folder under the package name.

## Requirements

**Python 3**
- `lxml import etree`
- `re`
- `os`


## Setup and Installation

1. **Clone the Repository:**

    ```sh
    git clone https://IrwinMitchell@dev.azure.com/IrwinMitchell/Trusted%20Data%20Platform/_git/data--tdp--dtsx-sql-query-extract
    cd "data--tdp--dtsx-sql-query-extract"
    ```

2. **Install Dependencies:**
   It's recommended to use a virtual environment (ensure you are in the root project folder "data--tdp--dtsx-sql-query-extract")

    ```sh
    python -m venv venv
    venv/Scripts/activate
    pip install -r requirements.txt
    ```

### Understanding the Script
  DTSX files contain SQL queries within both Data Flow and Exectue SQL tasks. The XML structures are as follows:

1. **Execute SQL Task Hirarchy:**

    SQL query is located in `SQLTask:SqlStatementSource` element.


     ```xml
     <DTS:Executable
          DTS:refId="Package\Failure\SQL_Test"
          DTS:Description="Execute SQL Task"
          DTS:ExecutableType="Microsoft.ExecuteSQLTask"
          DTS:ObjectName="SQL_Test"
          DTS:ThreadHint="0">
          <DTS:ObjectData>
            <SQLTask:SqlTaskData
              SQLTask:Connection="{DBE94BD0-09CC-4188-85DA-F3EE71F7C6A1}"
              SQLTask:SqlStatementSource="SELECT * FROM Test.Table;" xmlns:SQLTask="www.microsoft.com/sqlserver/dts/tasks/sqltask">
            </SQLTask:SqlTaskData>
          </DTS:ObjectData>
      </DTS:Executable>
     ```

2. **Data Flow Task Hirarchy:**

    SQL query is located between the property element, where `name="SqlCommand"`.


     ```xml
     <DTS:Executable
          DTS:refId="Package\Failure\SQL_Test"
          DTS:Description="Execute SQL Task"
          DTS:ExecutableType="Microsoft.ExecuteSQLTask"
          DTS:ObjectName="SQL_Test"
          DTS:ThreadHint="0">
       <DTS:ObjectData>
          <pipeline>
              <components>
                  <component>
                      <properties>
                          <property 
                              dataType="System.String"
                              description="The SQL command to be executed."
                              name="SqlCommand">
                                 SELECT * FROM Test.Table;
                          </property>
                      </properties>
                  </component>
              </components>
          </pipeline>
       </DTS:ObjectData>
      </DTS:Executable>
     ```

The script loops over the elements in these structures and extracts the sql queries into seperate files.

## Usage

### Run the Script

Runing the script with Python:

```sh
python main.py 
```
After execution, the script requires the user to input the file path of the dtsx file to be scraped e.g., `dtsx_files/<my_dtsx_file>`. If the file cannot be found, an error will be thrown.

## Common Issues
The sql queries are stored in files and directories replicating the structure of  objects in an SSIS package. If the directories are too many levels deep, an error could be thrown. Folder names are limited to 20 characters in an attempt to bypass this issue. To change this, go the the `create_folder()` function and alter the number of characters.

```py
def create_folder(path):
    folder_path = truncate_path(path, 20)
```

### Saving Files

SQL files are stored in `sql_scripts/<package_name>`


