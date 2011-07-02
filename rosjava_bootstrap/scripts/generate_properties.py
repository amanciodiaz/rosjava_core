#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys

import roslib.rosenv
import roslib.packages
import roslib.stacks

from generate_msg_depends import msg_jar_file_path, is_msg_pkg, is_srv_pkg

def usage():
    print "generate_properties.py <package-name>"
    sys.exit(os.EX_USAGE)
    
def resolve_pathelements(pathelements):
    # TODO: potentially recognize keys like ROS_HOME
    return [os.path.abspath(p) for p in pathelements]

def get_classpath(package):
    rospack = roslib.packages.ROSPackages()
    depends = rospack.depends([package])[package]
    pathelements = []
    tag = 'rosjava-pathelement'
        
    for pkg in depends:
        m = rospack.manifests[pkg]
        pkg_dir = roslib.packages.get_pkg_dir(pkg)
        for e in [x for x in m.exports if x.tag == tag]:
            try:
                pathelements.append(os.path.join(pkg_dir, e.attrs['location']))
            except KeyError:
                print >> sys.stderr, "Invalid <%s> tag in package %s"%(tag, pkg)
        if is_msg_pkg(pkg) or is_srv_pkg(pkg):
            pathelements.append(msg_jar_file_path(pkg))
    return os.pathsep.join(resolve_pathelements(pathelements))

def get_src_path(package, src=False):
    rospack = roslib.packages.ROSPackages()
    depends = rospack.depends([package])[package]
    elements = []
    tag = 'rosjava-src'
        
    m = rospack.manifests[package]
    pkg_dir = roslib.packages.get_pkg_dir(package)
    for e in [x for x in m.exports if x.tag == tag]:
        try:
            elements.append(os.path.join(pkg_dir, e.attrs['location']))
        except KeyError:
            print >> sys.stderr, "Invalid <%s> tag in package %s"%(tag, pkg)
    return os.pathsep.join(resolve_pathelements(elements))

def generate_properties_main(argv=None):
    if argv is None:
        argv = sys.argv
    use_eclipse = False
    if '--eclipse' in argv:
        use_eclipse = True
        argv = [a for a in argv if a != '--eclipse']
    if len(argv) != 2:
        usage()
    package = argv[1]
    if not use_eclipse:
        sys.stdout.write('ros.home=%s\n'%(roslib.rosenv.get_ros_home()))
        sys.stdout.write('ros.rosjava.dir=%s\n'%(roslib.packages.get_pkg_dir('rosjava')))
        sys.stdout.write('ros.classpath=%s\n'%(get_classpath(package).replace(':', '\:')))
        # re-encode for ant <fileset includes="${ros.jarfileset}">
        sys.stdout.write('ros.jarfileset=%s\n'%(get_classpath(package).replace(':', ',')))
        sys.stdout.write('ros.test_results=%s\n'%(os.path.join(roslib.rosenv.get_test_results_dir(), package)))
    else:
        sys.stdout.write("""<?xml version="1.0" encoding="UTF-8"?>
<classpath>
""")
        for p in get_src_path(package).split(':'):
            if p:
                sys.stdout.write('\t<classpathentry kind="src" path="%s"/>\n'%(p))
        sys.stdout.write("""\t<classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
	<classpathentry kind="con" path="org.eclipse.jdt.junit.JUNIT_CONTAINER/4"/>
""")
        for p in get_classpath(package).split(':'):
            if p:
                sys.stdout.write('\t<classpathentry kind="lib" path="%s"/>\n'%(p))
        sys.stdout.write("""\t<classpath kind="output" path="build"/>
</classpath>
""")
    
if __name__ == '__main__':
    generate_properties_main()