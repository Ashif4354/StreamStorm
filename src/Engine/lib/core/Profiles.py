from os import makedirs, listdir
from os.path import exists, join
from shutil import copytree, rmtree, Error
from platformdirs import user_data_dir
from concurrent.futures import ThreadPoolExecutor
from logging import Logger, getLogger

from .UndetectedDrivers import UndetectedDrivers

logger: Logger = getLogger(f"streamstorm.{__name__}")

class Profiles:
    __slots__: tuple[str, ...] = ('app_data_dir', 'profiles_dir', 'base_profile_dir')
    
    def __init__(self) -> None:
        
        self.app_data_dir: str = user_data_dir("StreamStorm", "DarkGlance")
        self.profiles_dir: str = self.__get_profiles_dir()
        self.base_profile_dir: str = self.__get_base_profile_dir()


    def __get_profiles_dir(self) -> str:
        return join(self.app_data_dir, "ChromiumProfiles")


    def __get_base_profile_dir(self) -> str:
        return join(self.profiles_dir, "BaseProfile")


    def get_available_temp_profiles(self, for_deletion: bool = False) -> list[str]:
        temp_profiles: list[str] = [
            profile for profile in listdir(self.profiles_dir) if profile.startswith("temp_profile_")
        ]
        
        no_of_profiles: int = len(temp_profiles)

        if not for_deletion and no_of_profiles != 0:
            for i in range(1, no_of_profiles + 1):
                if f'temp_profile_{i}' not in temp_profiles:
                    raise ValueError(f"temp_profile_{i} is missing. Try rebuilding the environment.")
        
        return temp_profiles

    def get_profile_dir(self, index: int, profiles: list[str]) -> str:

        index %= len(profiles)
        tempdir: str = join(self.profiles_dir, profiles[index])

        return tempdir
    
    def __delete_profiles_dir(self) -> None:
        if exists(self.profiles_dir):
            rmtree(self.profiles_dir, ignore_errors=True)
            logger.info(f"Profiles directory {self.profiles_dir} deleted.")

    def __create_base_profile(self) -> None:
        if exists(self.base_profile_dir):
            rmtree(self.base_profile_dir)        
        
        makedirs(self.base_profile_dir, exist_ok=True)

        UD: UndetectedDrivers = UndetectedDrivers(self.base_profile_dir)
        UD.initiate_base_profile()
        UD.youtube_login()

    def __create_profile(self, profile: str) -> None:

        logger.info(f"Creating {profile}")

        tempdir: str = join(self.profiles_dir, profile)

        makedirs(tempdir, exist_ok=True)
        
        try:
            copytree(
                self.base_profile_dir,
                tempdir,
                dirs_exist_ok=True,
            )
            
        except Error as e:
            str_error: str = str(e)
            logger.error(f"Error occurred while creating {profile}: {str_error}")

        logger.info(f"{profile} created")

    def create_profiles(self, count: int) -> None:
        self.__delete_profiles_dir()
        self.__create_base_profile()
        
        profiles: list[str] = [f"temp_profile_{i}" for i in range(1, count + 1)]
        
        with ThreadPoolExecutor() as executor:
            executor.map(self.__create_profile, profiles)
                
            
    def delete_all_temp_profiles(self) -> None:
        
        self.__delete_profiles_dir()

__all__: list[str] = ["Profiles"]