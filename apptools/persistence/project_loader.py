# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
# Standard library imports
import sys
import pickle
import logging

# Enthought library imports
from apptools.persistence.versioned_unpickler import VersionedUnpickler


logger = logging.getLogger(__name__)


def load_project(
    pickle_filename, updater_path, application_version, protocol, max_pass=-1
):
    """Reads a project from a pickle file and if necessary will update it to
    the latest version of the application.
    """

    latest_file = pickle_filename

    # Read the pickled project's metadata.
    f = open(latest_file, "rb")
    metadata = VersionedUnpickler(f).load(max_pass)
    f.close()
    project_version = metadata.get("version", False)

    if not project_version:
        raise ValueError("Could not read version number from the project file")

    logger.debug(
        "Project version: %d, Application version: %d"
        % (project_version, application_version)
    )

    # here you can temporarily force an upgrade each time for testing ....
    # project_version = 0
    latest_file = upgrade_project(
        pickle_filename,
        updater_path,
        project_version,
        application_version,
        protocol,
        max_pass,
    )

    # Finally we can import the project ...
    logger.info("loading %s" % latest_file)
    i_f = open(latest_file, "rb")
    project = VersionedUnpickler(i_f).load(max_pass)
    i_f.close()

    return project


def upgrade_project(
    pickle_filename,
    updater_path,
    project_version,
    application_version,
    protocol,
    max_pass=-1,
):
    """Repeatedly read and write the project to disk updating it one version
    at a time.

    Example the p5.project is at version 0
    The application is at version 3

    p5.project    --- Update1 ---> p5.project.v1
    p5.project.v1 --- Update2 ---> p5.project.v2
    p5.project.v2 --- Update3 ---> p5.project.v3
    p5.project.v3 ---> loaded into app

    The user then has the option to save the updated project as p5.project
    """
    first_time = True
    latest_file = pickle_filename

    # update the project until it's version matches the application's
    while project_version < application_version:

        next_version = project_version + 1

        if first_time:
            i_f = open(pickle_filename, "rb")
            data = i_f.read()
            open("%s.bak" % pickle_filename, "wb").write(data)
            i_f.seek(0)  # rewind the file to the start
        else:
            name = "%s.v%d" % (pickle_filename, project_version)
            i_f = open(name, "rb")
            latest_file = name

        logger.info("converting %s" % latest_file)

        # find this version's updater ...
        updater_name = "%s.update%d" % (updater_path, next_version)
        __import__(updater_name)
        mod = sys.modules[updater_name]
        klass = getattr(mod, "Update%d" % next_version)
        updater = klass()

        # load and update this version of the project
        project = VersionedUnpickler(i_f, updater).load(max_pass)
        i_f.close()

        # set the project version to be the same as the updater we just
        # ran on the unpickled files ...
        project.metadata["version"] = next_version

        # Persist the updated project ...
        name = "%s.v%d" % (pickle_filename, next_version)
        latest_file = name
        o_f = open(name, "wb")
        pickle.dump(project.metadata, o_f, protocol=protocol)
        pickle.dump(project, o_f, protocol=protocol)
        o_f.close()

        # Bump up the version number of the pickled project...
        project_version += 1
        first_time = False

    return latest_file
