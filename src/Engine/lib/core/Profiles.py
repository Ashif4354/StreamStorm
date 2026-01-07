from os import makedirs, listdir
from os.path import exists, join
from shutil import copytree, rmtree, Error
from platformdirs import user_data_dir
from concurrent.futures import ThreadPoolExecutor
from logging import Logger, getLogger

from .UndetectedDrivers import UndetectedDrivers
from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

class Profiles:
    __slots__: tuple[str, ...] = ('app_data_dir', 'environment_dir', 'base_profile_dir')
    
    def __init__(self) -> None:
        
        self.app_data_dir: str = user_data_dir("StreamStorm", "DarkGlance")
        self.environment_dir: str = self.__get_environment_dir()
        self.base_profile_dir: str = self.__get_base_profile_dir()


    def __get_environment_dir(self) -> str:
        return join(self.app_data_dir, "Environment")


    def __get_base_profile_dir(self) -> str:
        return join(self.environment_dir, "BaseProfile")


    def get_available_temp_profiles(self, for_deletion: bool = False, total_channels: int = 0, from_mcp: bool = False) -> list[str]:

        if settings.login_method == "cookies" and not from_mcp:
            # When using cookies method, profiles will not be already created, 
            # so we are mocking values twice the size of all channels in the users youtube account
            # Why twice? Because to avoid potential index errors and to be safe.
            logger.debug(f"Mocking {total_channels * 2} profiles")
            return [f"temp_profile_{i}" for i in range(1, total_channels * 2)]
        
        temp_profiles: list[str] = [
            profile for profile in listdir(self.environment_dir) if profile.startswith("temp_profile_")
        ]
        
        no_of_profiles: int = len(temp_profiles)

        if not for_deletion and no_of_profiles != 0:
            for i in range(1, no_of_profiles + 1):
                if f'temp_profile_{i}' not in temp_profiles:
                    raise ValueError(f"temp_profile_{i} is missing. Try logging in again.")
        
        return temp_profiles

    def get_profile_dir(self, index: int, profiles: list[str]) -> str:

        index %= len(profiles)
        tempdir: str = join(self.environment_dir, profiles[index])

        return tempdir
    
    def __delete_environment_dir(self) -> None:
        if exists(self.environment_dir):
            rmtree(self.environment_dir, ignore_errors=True)
            logger.info(f"Environment directory {self.environment_dir} deleted.")

    def __create_base_profile(self, cookies: list | None = None) -> None:
        if exists(self.base_profile_dir):
            rmtree(self.base_profile_dir)        
        
        makedirs(self.base_profile_dir, exist_ok=True)

        UD: UndetectedDrivers = UndetectedDrivers(self.base_profile_dir)
        UD.initiate_base_profile(cookies)
        UD.youtube_login()

    def __create_profile(self, profile: str) -> None:

        logger.info(f"Creating {profile}")

        tempdir: str = join(self.environment_dir, profile)

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

    def create_profiles(self, count: int, cookies: list | None = None) -> None:
        self.__delete_environment_dir()
        self.__create_base_profile(cookies)

        if settings.login_method == "cookies":
            return
        
        profiles: list[str] = [f"temp_profile_{i}" for i in range(1, count + 1)]
        
        with ThreadPoolExecutor() as executor:
            executor.map(self.__create_profile, profiles)
                
    def delete_all_temp_profiles(self) -> None:
        
        self.__delete_environment_dir()

__all__: list[str] = ["Profiles"]
