import os
import os.path
from lxml import etree
import random
import re

############################################################################################################
#  VARIABLES
############################################################################################################

file_count = 0 
file_exists = 0
file_fail = 0

# Define the tags we needs to search the SSIS package for (all unique tags available in ele_tags variable)
pfx = '{www.microsoft.com/'
ref_tag = pfx + 'SqlServer/Dts}refId'
exe_tag = pfx + 'SqlServer/Dts}Executable'
obj_tag = pfx + 'SqlServer/Dts}ObjectName'
dat_tag = pfx + 'SqlServer/Dts}ObjectData'
tsk_tag = pfx + 'sqlserver/dts/tasks/sqltask}SqlTaskData'
src_tag = pfx + 'sqlserver/dts/tasks/sqltask}SqlStatementSource'
desc_tag = pfx + 'SqlServer/Dts}Description'
###########################################################################################################

# Read the dtxx file and get the root objects
def read_and_parse_file():
    # set dtsx package file
    ssis_dtsx = input("Please enter the .dtsx file path: ") #rf'dtsx_files/HR_DataConductor.dtsx'
    # If the file doesn't exist, raise an error, else return the root objects
    if not os.path.isfile(ssis_dtsx):
        raise("File Does Not Exist")
    else:
        # read and parse ssis package
        tree = etree.parse(ssis_dtsx)
        root = tree.getroot()
        print('SSIS Package Found: ' + f'{root.attrib[obj_tag]}') 

        # Return the root object
        return root

# Truncates file path lengths
def truncate_path(path, max_length):
    # Split the path by backslashes so they become individual phrases
    parts = path.split('\\')
    # Strip leading spaces and truncate each part to the specified max length
    truncated_parts = [part[:max_length].strip() for part in parts]
    # Join the parts back together with backslashes
    truncated_path = '\\'.join(truncated_parts).strip()
    # return
    return truncated_path

# Removes some special characters and extra whitespaces
def clean_string(input_string):
    # Split the path by backslashes so they become individual phrases
    #parts = input_string.split('\\')
    # Use re.sub() to remove special characters, except (, ), _, - and remove extra whitespaces
    #cleaned_parts = [re.sub(r'\s{2,}', ' ', re.sub(r'[^A-Za-z0-9\ ]+', '', part)).strip() for part in parts] #'[^A-Za-z0-9 \-\_\(\)]+'
    # Join the parts back together with backslashes
    cleaned_string = re.sub(r'\s{2,}', ' ', re.sub(r'[^A-Za-z0-9\ \\]+', ' ', input_string)).replace(' ', '_').strip()
    #cleaned_string = '\\'.join(cleaned_parts)
    # return          
    return cleaned_string

# Creates folder structure if doesn't exist
def create_folder(path):
    # Truncate the folder path
    folder_path = truncate_path(path, 20)
    # Clean the folder path
    folder_path = clean_string(folder_path).replace(' ', '_')
    # Create the directory structure if it doesnt exist
    os.makedirs(os.path.dirname(f'{folder_path}\\'), exist_ok=True)
    # Return
    return folder_path

# Creates file if doesn't exist
def create_file(full_path, file_content, ssis_path):
    global file_count
    global file_exists
    global file_fail
    try:
        # If file already exists
        if os.path.isfile(full_path):

            file_exists += 1
            print(f'File already exists: {full_path}')

        else:
            # Write to SQL file
            with open(full_path, "w") as file: 
                file.write(f'-- SSIS Location: {ssis_path}\n')
                file.write(file_content) 
            
            # Add to file count
            file_count += 1
            print(f'File successfully created: {full_path}')

    except Exception as e:
        file_fail += 1
        print(f"Failed to create file {full_path}: {e}")


# Extracts sql queries from a data flow task
def extract_data_flow_task(objects, folder_path, id, object_name): 
    for pipeline in objects:
        for components in pipeline:
            for component in components:
                # Get the name of the SSIS object
                component_obj_name = component.attrib["name"].strip()
                ssis_path = component.attrib["refId"].strip()
                for properties in component:
                    for property in properties:
                        # If the property object contains the name attribute with a value of 'SqlCommand'
                        # Sometimes there is no text between the property tags
                        if property.attrib['name'] == 'SqlCommand' and property.text is not None: 
                                
                            # Create the directory structure if it doesnt exist
                            folder_path = create_folder(f'{folder_path}')#\\{component_obj_name}') 

                            clean_file_name = clean_string(f'{id}_DF_{component_obj_name}') #{object_name[:10]}

                            create_file(full_path=f'{folder_path}\\{clean_file_name}.sql', file_content=property.text, ssis_path={ssis_path})


def main():
    # Return root objects from dtsx file and store in root variable
    root = read_and_parse_file()

    # Get the name of the SSIS package
    package_name = root.attrib[obj_tag].replace(" ","")

    # Loop over the root tags in the XML file
    for cnt, ele in enumerate(root.xpath(".//*")):
        # If the element (ele) tag = 'Executable'
        if ele.tag == exe_tag:
            
            # Gets all attributes within Executable tag e.g. {'{www.microsoft.com/SqlServer/Dts}refId': 'Package\\SEQ_Loader\\HR Data Conductor\\Cost of Absence\\CostOfAbsence_Sickness Table', '{www.microsoft.com/SqlServer/Dts}CreationName':}
            attr = ele.attrib

            # Extract the refId from the Executable object {}
            refid = attr[ref_tag].strip()
            
            # Go 1 directory level higher e.g. 'Package\\SEQ_Loader\\HR Data Conductor\\Cost of Absence\\CostOfAbsence_Sickness Table' = 'Package\\SEQ_Loader\\HR Data Conductor\\Cost of Absence'
            trunc_refid = "\\".join(refid.split("\\")[:-1]).strip()

            # Get the task name (description)
            taskName = attr[desc_tag].strip()

            # Generate a random number between 0 and 10000000
            ran_no = random.randint(0, 10000000)

            object_id = cnt

            # Clean folder string to remove some special characters & extra whitespaces
            folder_path = f'sql_scripts\\{package_name}\\{trunc_refid}'       

            # Loop over the Executable object and locate the ObjectData attribute
            for objects in ele:
                # If the tag = ObjectData, loop over the items in that tag 
                if objects.tag == dat_tag:
                    # Get the name of the parent SSIS object
                    object_name = attr[obj_tag].strip()
                    # If the task is a Data Flow Task, it has a different XML structure
                    if taskName == 'Data Flow Task':
                        extract_data_flow_task(objects, folder_path, object_id, object_name)#, file_name=f'{object_id}_{parent_obj_name}-{ran_no}.sql')
                                                    
                    # elif the task is an Execute SQL Task, it has a different XML structure
                    elif taskName == 'Execute SQL Task':
                        for sql_task in objects:
                            # Get the sql query from the SqlStatementSource tag
                            sql_task_query = sql_task.get(src_tag)
                            
                            # Create the directory structure if it doesnt exist
                            folder_path = create_folder(folder_path) 

                            clean_file_name = clean_string(f'{object_id}_ES_{object_name}')

                            # Write to SQL file
                            create_file(full_path=f'{folder_path}\\{clean_file_name}.sql', file_content=sql_task_query, ssis_path=refid) 
    
    print(f"Files created: {file_count}, Files already exist: {file_exists}, Files failed: {file_fail}")

main()

#"File already exists: sql_scripts\HR_DataConductor\Package\SEQ_Loader\HR Data Conductor\Sequence Container\Balanced Scorecard\Sequence Container\28131_BSC - Calculated Metrics-85309.sql"