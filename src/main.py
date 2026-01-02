from typing import Optional, Tuple
from google.cloud import storage
from google.cloud.storage import Blob
from json import loads, dumps
from dataclasses import dataclass, field

#Dataclass for storing instances of variables. A full class isn't quite needed here. (Maybe in the future.)
@dataclass
class StorageState:
    client: Optional[storage.Client] = None
    bucket_name: Optional[str] = None
    bucket: Optional[storage.Bucket] = None
    blob_name: Optional[str] = "notes.json"
    blob_r:Optional[Blob] = None
    id_count: int = 0
    old_ids:list[int] = field(default_factory=list)

state = StorageState()

def catch_errors(func):
    """Wrapper that handles try/except in functions using the specified Tuple schema.

    Args:
        func (function): name of the function to wrap. Usually automatic with the @ syntax.
    """
    def catch(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            return (False, str(e))
    return catch

def setup(bucket_n:Optional[str]) -> Tuple[bool, Optional[str]]:
    """Function to set up storage

    Args:
        bucket_n (str): Bucket name. 

    Returns:
        Tuple[bool, Optional[str]]: 
    """

    #Make sure we have bucket name.
    if bucket_n is None:
        return (False,"No bucket name provided.")
    
    #Check the bucket name.
    ok, err = check_string(bucket_n)
    if not ok:
        return (False, str(err))
    
    #Set up our stuff
    try:
        #Get the client
        state.client = storage.Client()

        #Set the state of our client
        state.bucket_name = bucket_n

        #Attach our bucket to the client.
        state.bucket = state.client.bucket(state.bucket_name)

        #Attach our blob
        state.blob_r = state.bucket.blob(state.blob_name)

    except Exception as e:

        #Return to our default state
        state.client = None
        state.bucket_name = ""
        state.bucket = None
        state.blob_r = None

        return (False,str(e))
    
    return (True,None)

@catch_errors
def add_note(title:str,content:str) -> Tuple[bool,Optional[str]]:
    """Function that adds notes to the cloud storage via JSON.

    Args:
        title (str): _description_
        content (str): _description_

    Returns:
        Tuple[bool,Optional[str]]: A bool, indicating success or failure of the operation. The str is an error message(if no error, it is None).
    """

    #Check title
    ok,err = check_string(title)
    if not ok:
        return (False,str(err))
    
    #Check Content
    ok, err = check_string(content)
    if not ok:
        return (False,str(err))

    
    #Check to see if setup was called.
    if state.client is None or state.blob_r is None:
        return (False, "Setup hasn't run yet.")
    
    else:
            #Get the notes.
            notes = loads(state.blob_r.download_as_text())

            #Get the id
            note_id = generate_id()

            #Modify the notes we have downloaded.
            notes[str(note_id)] = {"title":title,"content":content}

            #Upload
            state.blob_r.upload_from_string(dumps(notes))
        

        
    return (True,None)

    

def generate_id() -> int:
    """Function to generate or take an id from entries that have been deleted.

    Returns:
        int: The Id which has been chosen.
    """
    #Check to see if there are any pre-used ids.
    if len(state.old_ids) != 0:

        back = state.old_ids[0]
        del state.old_ids[0]
        
        return back
    
    #No pre-used ids. Generate new.
    else:
        
        back = state.id_count
        
        state.id_count += 1

        return back

def check_int_positive(*args:Optional[int]) -> Tuple[bool,Optional[str]]:
    """Function to check that an integer is valid for purposes of specifying id.

    Args:
        prospect (Optional[int]): The integer to check. 

    Returns:
        Tuple[bool,Optional[str]]: Bool indicating success of the function. The string is an error message (if any). Can be None if the function was successful.
    """

    if len(args) == 0:
        return (False,"Argument 0 is not provided.")

    for idx, i in enumerate(args):
        
        #Check that they are strings.
        if not isinstance(i,int):
            return (False,f"Argument {idx} is not an integer.")
        
        #Check that they are not negative.
        if i < 0:
            return (False,f"Argument {idx} is negative.")
        
    
    return (True,None)

def check_string(*args:Optional[str]) -> Tuple[bool,Optional[str]]:
    """_summary_

    Args:
        prospect (Optional[str]): String to check.

    Returns:
        Tuple[bool,Optional[str]]: Bool indicating success of the function. The string is an error message (if any). Can be None if the function was successful.
    """
    if len(args) == 0:
        return (False,"Argument 0 is not provided.")


    for idx, s in enumerate(args):

        #Check that they are strings.
        if not isinstance(s,str):
            return (False,f"Argument {idx} is not a string.")
        
        #Check that they are not empty.
        if len(s.strip()) == 0:
            return (False, f"Argument {idx} is empty.")

    
    #Checks out.
    return (True,None)



