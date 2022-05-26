from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = "2.1.3"
    
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    topics = ("jpeg", "libjpeg", "image", "multimedia", "format", "graphics")
    url = "https://gitlab.worldiety.net/worldiety/customer/wdy/libriety/cpp/forks"    
    homepage = "https://libjpeg-turbo.org"
    license = "BSD-3-Clause, Zlib"
    provides = "libjpeg"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "SIMD": [True, False],
        "arithmetic_encoder": [True, False],
        "arithmetic_decoder": [True, False],
        "libjpeg7_compatibility": [True, False],
        "libjpeg8_compatibility": [True, False],
        "mem_src_dst": [True, False],
        "turbojpeg": [True, False],
        "enable12bit": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "SIMD": True,
        "arithmetic_encoder": True,
        "arithmetic_decoder": True,
        "libjpeg7_compatibility": True,
        "libjpeg8_compatibility": True,
        "mem_src_dst": True,
        "turbojpeg": False,
        "enable12bit": False,
    }

    no_copy_source = True    
    exports_sources = "*", "!autom4te.cache"
    python_requires = "wdyConanHelper/[]"
    python_requires_extend = "wdyConanHelper.ConanCMake"


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

        if self.options.enable12bit:
            del self.options.java
            del self.options.turbojpeg
        if self.options.enable12bit or self.settings.os == "Emscripten":
            del self.options.SIMD
        if self.options.enable12bit or self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility:
            del self.options.arithmetic_encoder
            del self.options.arithmetic_decoder
        if self.options.libjpeg8_compatibility:
            del self.options.mem_src_dst

    def validate(self):
        if self.options.enable12bit and (self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility):
            raise ConanInvalidConfiguration("12-bit samples is not allowed with libjpeg v7/v8 API/ABI")

    @property
    def _is_arithmetic_encoding_enabled(self):
        return self.options.get_safe("arithmetic_encoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    @property
    def _is_arithmetic_decoding_enabled(self):
        return self.options.get_safe("arithmetic_decoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    def build_requirements(self):
        if self.options.get_safe("SIMD") and self.settings.arch in ["x86", "x86_64"]:
            self.build_requires("nasm/[]")

    def cmake_definitions(self):
        defs = {
            "ENABLE_STATIC": not self.options.shared,
            "ENABLE_SHARED": self.options.shared,
            "WITH_SIMD": self.options.get_safe("SIMD", False),
            "WITH_ARITH_ENC": self._is_arithmetic_encoding_enabled,
            "WITH_ARITH_DEC": self._is_arithmetic_decoding_enabled,
            "WITH_JPEG7": self.options.libjpeg7_compatibility,
            "WITH_JPEG8": self.options.libjpeg8_compatibility,
            "WITH_MEM_SRCDST": self.options.get_safe("mem_src_dst", False),
            "WITH_TURBOJPEG": self.options.get_safe("turbojpeg", False),
            "WITH_12BIT": self.options.enable12bit,
            "CMAKE_C_FLAGS": "-fexceptions",
            "ld-version-script": False,
            "BUILD_TESTING": False,
        }
        

#        if tools.cross_building(self):
#            # TODO: too specific and error prone, should be delegated to a conan helper function
#            cmake_system_processor = {
#                "armv8": "aarch64",
#                "armv8.3": "aarch64",
#            }.get(str(self.settings.arch), str(self.settings.arch))
#            self._cmake.definitions["CONAN_LIBJPEG_SYSTEM_PROCESSOR"] = cmake_system_processor
        return defs
