from fastapi import Depends
from typing import Annotated


SettingsDep = Annotated[Settings, Depends(get_settings)]
ServiceDep = Annotated[Settings, Depends(get_settings)]
