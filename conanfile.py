from conans import ConanFile, CMake, tools, Meson
import os

class JsonglibConan(ConanFile):
    name = "json-glib"
    version = "1.4.4"
    description = "JSON-GLib implements a full suite of JSON-related tools using GLib and GObject."
    url = "https://github.com/conan-multimedia/json-glib"
    homepage = "https://github.com/GNOME/json-glib"
    license = "LGPLv2_1Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = ("libffi/3.3-rc0@conanos/dev", "glib/2.58.0@conanos/dev", "gobject-introspection/1.58.0@conanos/dev")
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("https://github.com/GNOME/{name}/archive/{version}.tar.gz".format(name=self.name, version =self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'LD_LIBRARY_PATH':'%s/lib'%(self.deps_cpp_info["libffi"].rootpath),
                'PATH':'%s/bin:%s'%(self.deps_cpp_info["gobject-introspection"].rootpath, os.getenv("PATH"))
                }):
                meson = Meson(self)
                meson.configure(
                    defs={ 'disable_introspection':'false',
                           'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
                         },
                    source_dir = '%s'%(os.getcwd()),
                    build_dir= '%s/builddir'%(os.getcwd()),
                    pkg_config_paths=[ '%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["glib"].rootpath),
                                       '%s/lib/pkgconfig'%(self.deps_cpp_info["gobject-introspection"].rootpath),
                                       ]
                                )
                meson.build(args=['-j4'])
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

