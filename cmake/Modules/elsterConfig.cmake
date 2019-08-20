INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_ELSTER elster)

FIND_PATH(
    ELSTER_INCLUDE_DIRS
    NAMES elster/api.h
    HINTS $ENV{ELSTER_DIR}/include
        ${PC_ELSTER_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    ELSTER_LIBRARIES
    NAMES gnuradio-elster
    HINTS $ENV{ELSTER_DIR}/lib
        ${PC_ELSTER_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/elsterTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ELSTER DEFAULT_MSG ELSTER_LIBRARIES ELSTER_INCLUDE_DIRS)
MARK_AS_ADVANCED(ELSTER_LIBRARIES ELSTER_INCLUDE_DIRS)
