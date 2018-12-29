from conans import ConanFile, tools, Meson
from conanos.build import config_scheme
import os, shutil

class JsonglibConan(ConanFile):
    name = "json-glib"
    version = "1.4.4"
    description = "JSON-GLib implements a full suite of JSON-related tools using GLib and GObject."
    url = "https://github.com/conanos/json-glib"
    homepage = "https://github.com/GNOME/json-glib"
    license = "LGPL-v2.1+"
    exports = ["json-gobject.c","json-gvariant.c","json-path.c","json-reader.c","json-node.c"]
    generators = "gcc","visual_studio"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    #requires = ("libffi/3.3-rc0@conanos/dev", "glib/2.58.0@conanos/dev", "gobject-introspection/1.58.0@conanos/dev")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")

    def build_requirements(self):
        self.build_requires("libffi/3.299999@conanos/stable")
        self.build_requires("zlib/1.2.11@conanos/stable")

    def source(self):
        url_= "https://github.com/GNOME/json-glib/archive/{version}.tar.gz"
        tools.get(url_.format(version =self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            for i in self.exports:
                shutil.copy2(os.path.join(self.source_folder,i),
                             os.path.join(self.source_folder,self._source_subfolder,"json-glib",i))

    def build(self):
        deps=["glib","libffi","zlib"]
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in deps ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        
        if self.settings.os == 'Windows':
            defs.update({'introspection':'false'})
        binpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["glib"] ]
        
        meson = Meson(self)
        #if self.settings.os == 'Linux':
        #    with tools.chdir(self.source_subfolder):
        #        with tools.environment_append({
        #            'LD_LIBRARY_PATH':'%s/lib'%(self.deps_cpp_info["libffi"].rootpath),
        #            'PATH':'%s/bin:%s'%(self.deps_cpp_info["gobject-introspection"].rootpath, os.getenv("PATH"))
        #            }):
        #            
        #            meson.configure(
        #                defs={ 'disable_introspection':'false',
        #                       'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
        #                     },
        #                source_dir = '%s'%(os.getcwd()),
        #                build_dir= '%s/builddir'%(os.getcwd()),
        #                pkg_config_paths=[ '%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
        #                                   '%s/lib/pkgconfig'%(self.deps_cpp_info["glib"].rootpath),
        #                                   '%s/lib/pkgconfig'%(self.deps_cpp_info["gobject-introspection"].rootpath),
        #                                   ]
        #                            )
        #            meson.build(args=['-j4'])
        #            self.run('ninja -C {0} install'.format(meson.build_dir))

        if self.settings.os == 'Windows':
            with tools.environment_append({
                'PATH' : os.pathsep.join(binpath + [os.getenv('PATH')]),
                }):
                meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                                pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir/install"%(os.getcwd()))
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

