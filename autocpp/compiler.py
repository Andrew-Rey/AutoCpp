import os
import sys
import subprocess
import logging
from os import path
from typing import Dict
from logging import handlers
from .cxxproject import CxxProject
from .cmake_tools import CMakeTools
from datamap import *


class Compiler(object):

    def __init__(self, configs: Dict) -> None:
        self.compiler_configs: CompilerConfig = configs[ConfigKey._CompilerKey_]
        self.cmake_configs: CMakeConfig = configs[ConfigKey._CMakeKey_]

        self.cmake_tool: CMakeTools = CMakeTools()

    def _add_cmake_contents(self, content: str):
        self.cmake_tool.cmake_contents.append(content)

    def _add_cmake_cli(self, key: str, cli: str):
        self.cmake_tool.set_cli(key, cli, False)

    def cmake_init(self, project: CxxProject):
        """init cmake_lists contents and cmake command lines"""
        if project.multifile:
            main_file = project.main_file
            lib_files = ""
            files = [f for f in os.listdir(project.project_path) if len(f.split(".")) > 1]
            for file in files:
                if not file.split(".")[1] in CxxProject.CXX_EXT:
                    continue
                if file.split(".")[0] == "main":
                    self.main_file = self.PATH_SYMBOL.join((project.project_path, file))
                else:
                    file = self.PATH_SYMBOL.join((project.project_path, file))
                    lib_files += file
                    lib_files += " "
            self.cmake_tool.cmake_contents = self.cmake_tool.cmake_init_mul(main_file, lib_files, self.cmake_configs)
        else:
            self.cmake_tool.cmake_contents = self.cmake_tool.cmake_init_slg(main_file, self.cmake_configs)
        config_cmd = "-D CMAKE_BUILD_TYPE:STRING={}".format(self.compiler_configs.BuildType) + " " + \
            "-D CMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE" + " " + \
            "-D CMAKE_C_COMPILER:FILEPATH={}".format(self.compiler_configs.CCompilerPath) + " " + \
            "-D CMAKE_CXX_COMPILER:FILEPATH={}".format(self.compiler_configs.CXXCompilerPath) + " " + \
            "-S {}".format(project.project_path if project.multifile else project.project_path.split("/")[0:-1]) + " " + \
            "-B {}".format(self.compiler_configs.BuildPath) + " " + \
            "-G {}".format(self.compiler_configs.Genrator)
        build_cmd = "{}".format(self.compiler_configs.Genrator)
        run_cmd = ".{}/{}.exe".format(self.compiler_configs.BuildPath, self.cmake_configs.ProjectName)
        self.cmake_tool.set_cli("config", config_cmd)
        self.cmake_tool.set_cli("build", build_cmd)
        self.cmake_tool.set_cli("run", run_cmd)

        self.cmake_tool.cmake_lists(self.cmake_configs.CMakePath)

        print("CMakeList.txt has been written into {}".format(self.cmake_configs.CMakePath))
        print("CMake commands has been config:")
        print(self.cmake_tool.cmake_cli)

    def cmake_config(self):
        try:
            subprocess.call([
                self.cmake_configs.CMakePath,
                " " + self.cmake_tool.cmake_cli["config"]
            ])
        except OSError:
            print("cmake config error")

    def cmake_build(self):
        try:
            subprocess.call([
                self.cmake_configs.CMakePath,
                " " + self.cmake_tool.cmake_cli["build"]
            ])
        except OSError:
            print("cmake build error")

    def cmake_run(self):
        try:
            subprocess.call([
                self.cmake_configs.CMakePath,
                " " + self.cmake_tool.cmake_cli["run"]
            ])
        except OSError:
            print("cmake run error")
