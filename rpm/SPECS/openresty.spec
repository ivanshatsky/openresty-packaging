Name:           openresty
Version:        1.31.8.1
Release:        1%{?dist}
Summary:        OpenResty, scalable web platform by extending NGINX with Lua

Group:          System Environment/Daemons

# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:        BSD
URL:            https://openresty.org/

# the OpenResty build that the module sub-packages are tied to; the sub-packages
# override Version, so never use the plain version macro in their Requires
%global or_version  %{version}
%global or_evr      %{or_version}-%{release}

Source0:        https://openresty.org/download/openresty-%{version}.tar.gz

%if 0%{?amzn} >= 2 || 0%{?suse_version} || 0%{?fedora} || 0%{?rhel} >= 7 || "%{?_vendor}" == "mariner"
%define         use_systemd   1
%endif

Source1:        openresty.service
Source2:        openresty.init
Patch0:         openresty-nginx-conf-includes.patch

# Native Linux AIO support in nginx (--with-file-aio): built by default.
# Skip with: rpmbuild --without file_aio
%bcond_without file_aio

# build switches: all modules are built by default; skip all with --without modules,
# or one with --without brotli / --without zstd. With --without modules the defaults
# flip to off and a single module is added back with --with brotli / --with zstd.
%bcond_without modules
# per-module defaults follow the master switch; an explicit --with / --without still wins.
# One pair of lines per new module (on rpm 4.17.1+ one bcond line with an expression does it).
%if %{with modules}
%bcond_without brotli
%bcond_without zstd
%bcond_without njs
%bcond_without xslt
%bcond_without image_filter
%bcond_without perl
%bcond_without geoip2
%else
%bcond_with brotli
%bcond_with zstd
%bcond_with njs
%bcond_with xslt
%bcond_with image_filter
%bcond_with perl
%bcond_with geoip2
%endif

# third-party dynamic modules, pinned to commits or release tags
%global ngx_brotli_commit   53e0fb55f250f48fe80c0ddbf6c0f7103cdbaae1
%global ngx_brotli_date     20261022
%global ngx_brotli_short    %(echo %{ngx_brotli_commit} | cut -c1-7)
%global brotli_version      1.2.1
#%%global brotli_commit       db24a98aed38a16de78cc05ca15cdd8dc2a0d92d
# -fPIC is mandatory: the static brotli libs are linked into a shared object
%global brotli_cflags       -O3 -fPIC -ffunction-sections -fdata-sections

%global ngx_zstd_commit     057a7d339af1111d04b5a9ac5ae9b0250d17cd94
%global ngx_zstd_date       20250623
%global ngx_zstd_short      %(echo %{ngx_zstd_commit} | cut -c1-7)

%global njs_version         1.0.2
%global quickjs_commit      e585640ffa2cf88ce7c2d587583c6fe15928ec2f
%global quickjs_date        20261110
%global quickjs_version     20260604
%global quickjs_short       %(echo %{quickjs_commit} | cut -c1-7)
# -fPIC is mandatory: libquickjs.a is linked into shared objects
%global quickjs_cflags      -O2 -fPIC

%global ngx_geoip2_commit   a607a41a8115fecfc05b5c283c81532a3d605425
%global ngx_geoip2_date     20230614
%global ngx_geoip2_short    %(echo %{ngx_geoip2_commit} | cut -c1-7)
%global ngx_geoip2_version  3.4

Source10:       https://github.com/google/ngx_brotli/archive/%{ngx_brotli_commit}.tar.gz#/ngx_brotli-%{ngx_brotli_commit}.tar.gz
Source11:       https://github.com/google/brotli/archive/refs/tags/v%{brotli_version}.tar.gz#/brotli-%{brotli_version}.tar.gz
#Source11:       https://github.com/google/brotli/archive/%%{brotli_commit}.tar.gz#/brotli-%%{brotli_commit}.tar.gz

Source12:       https://github.com/tokers/zstd-nginx-module/archive/%{ngx_zstd_commit}.tar.gz#/zstd-nginx-module-%{ngx_zstd_commit}.tar.gz

Source13:       https://github.com/nginx/njs/archive/refs/tags/%{njs_version}.tar.gz#/njs-%{njs_version}.tar.gz
Patch13:        njs-configure-cc-with-args.patch
Source14:       https://github.com/bellard/quickjs/archive/%{quickjs_commit}.tar.gz#/quickjs-%{quickjs_commit}.tar.gz

Source15:       https://github.com/leev/ngx_http_geoip2_module/archive/%{ngx_geoip2_commit}.tar.gz#/ngx_http_geoip2_module-%{ngx_geoip2_commit}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  perl-File-Temp
BuildRequires:  ccache, gcc, make, perl, systemtap-sdt-devel
BuildRequires:  openresty-zlib-devel >= 1.3.2
BuildRequires:  openresty-openssl3-devel >= 3.5.9-1
BuildRequires:  openresty-pcre2-devel >= 10.47
BuildRequires:  kernel-headers
BuildRequires:  patch
%if %{with brotli}
BuildRequires:  cmake >= 3.15
%endif
%if %{with zstd}
BuildRequires:  libzstd-devel
%endif
%if %{with njs}
BuildRequires:  libxml2-devel
%endif
%if %{with xslt}
BuildRequires:  libxslt-devel
BuildRequires:  libxml2-devel
%endif
%if %{with image_filter}
BuildRequires:  gd-devel
%endif
%if %{with perl}
BuildRequires:  perl-devel
BuildRequires:  perl-ExtUtils-Embed
BuildRequires:  perl-ExtUtils-MakeMaker
%endif
%if %{with geoip2}
BuildRequires:  libmaxminddb-devel
%endif
Requires:       openresty-zlib >= 1.3.2
Requires:       openresty-openssl3 >= 3.5.9-1
Requires:       openresty-pcre2 >= 10.47


%if 0%{?suse_version}

# for /sbin/service
Requires(post):  insserv-compat
Requires(preun): insserv-compat

BuildRequires:  systemd

%else

%if 0%{?use_systemd}

BuildRequires:  systemd
Requires:       systemd

%else

# for /sbin/service
Requires(post):  chkconfig
Requires(preun): chkconfig, initscripts

%endif

%endif

AutoReqProv:        no

%define orprefix            %{_usr}/local/%{name}
%define zlib_prefix         %{orprefix}/zlib
%define pcre_prefix         %{orprefix}/pcre2
%define openssl_prefix      %{orprefix}/openssl3


%description
This package contains the core server for OpenResty. Built for production
uses.

OpenResty is a full-fledged web platform by integrating the standard Nginx
core, LuaJIT, many carefully written Lua libraries, lots of high quality
3rd-party Nginx modules, and most of their external dependencies. It is
designed to help developers easily build scalable web applications, web
services, and dynamic web gateways.

By taking advantage of various well-designed Nginx modules (most of which
are developed by the OpenResty team themselves), OpenResty effectively
turns the nginx server into a powerful web app server, in which the web
developers can use the Lua programming language to script various existing
nginx C modules and Lua modules and construct extremely high-performance
web applications that are capable to handle 10K ~ 1000K+ connections in
a single box.


%if 0%{?suse_version}

%debug_package

%else

# Remove source code from debuginfo package.
%define __debug_install_post \
    %{_rpmconfigdir}/find-debuginfo.sh %{?_missing_build_ids_terminate_build:--strict-build-id} %{?_find_debuginfo_opts} "%{_builddir}/%{?buildsubdir}"; \
    rm -rf "${RPM_BUILD_ROOT}/usr/src/debug"; \
    mkdir -p "${RPM_BUILD_ROOT}/usr/src/debug/openresty-%{or_version}"; \
    mkdir -p "${RPM_BUILD_ROOT}/usr/src/debug/tmp"; \
    mkdir -p "${RPM_BUILD_ROOT}/usr/src/debug/builddir"; \
%{nil}

%endif

%if 0%{?fedora} >= 27
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%endif

%if 0%{?rhel} >= 8
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%endif


%package resty

Summary:        OpenResty command-line utility, resty
Group:          Development/Tools
Requires:       perl, openresty >= %{version}-%{release}
Requires:       perl(File::Spec), perl(FindBin), perl(List::Util), perl(Getopt::Long), perl(File::Temp), perl(POSIX), perl(Time::HiRes)

%if 0%{?fedora} >= 10 || 0%{?rhel} >= 6 || 0%{?centos} >= 6
BuildArch:      noarch
%endif


%description resty
This package contains the "resty" command-line utility for OpenResty, which
runs OpenResty Lua scripts on the terminal using a headless NGINX behind the
scene.

OpenResty is a full-fledged web platform by integrating the standard Nginx
core, LuaJIT, many carefully written Lua libraries, lots of high quality
3rd-party Nginx modules, and most of their external dependencies. It is
designed to help developers easily build scalable web applications, web
services, and dynamic web gateways.


%package doc

Summary:        OpenResty documentation tool, restydoc
Group:          Development/Tools
Requires:       perl, perl(Getopt::Std), perl(File::Spec), perl(FindBin), perl(Cwd), perl(File::Temp), perl(Pod::Man), perl(Pod::Text)

%if (!0%{?rhel} || 0%{?rhel} < 7) && !0%{?fedora}
Requires:       groff
%endif

%if (0%{?rhel} && 0%{?rhel} >= 7) || 0%{?fedora}
Requires:       groff-base
%endif

Provides:       restydoc, restydoc-index, md2pod.pl

%if 0%{?fedora} >= 10 || 0%{?rhel} >= 6 || 0%{?centos} >= 6
BuildArch:      noarch
%endif


%description doc
This package contains the official OpenResty documentation index and
the "restydoc" command-line utility for viewing it.

OpenResty is a full-fledged web platform by integrating the standard Nginx
core, LuaJIT, many carefully written Lua libraries, lots of high quality
3rd-party Nginx modules, and most of their external dependencies. It is
designed to help developers easily build scalable web applications, web
services, and dynamic web gateways.


%package opm

Summary:        OpenResty Package Manager
Group:          Development/Tools
Requires:       perl, openresty >= %{version}-%{release}, perl(Digest::MD5)
Requires:       openresty-doc >= %{version}-%{release}, openresty-resty >= %{version}-%{release}
Requires:       curl, tar, gzip
#BuildRequires:  perl(Digest::MD5)
Requires:       perl(Encode), perl(FindBin), perl(File::Find), perl(File::Path), perl(File::Spec), perl(Cwd), perl(Digest::MD5), perl(File::Copy), perl(File::Temp), perl(Getopt::Long)

%if 0%{?fedora} >= 10 || 0%{?rhel} >= 6 || 0%{?centos} >= 6
BuildArch:      noarch
%endif


%description opm
This package provides the client side tool, opm, for OpenResty Pakcage Manager (OPM).


%if %{with brotli}
%package module-brotli
Version:        %{or_version}+1.0.0~rc^git%{ngx_brotli_date}.%{ngx_brotli_short}
# the main package sets AutoReqProv: no; the modules need their library requirements
AutoReqProv:    yes
Requires:       openresty = %{or_evr}
Provides:       bundled(brotli) = %{brotli_version}

Summary:        Brotli filter and static dynamic modules for OpenResty
License:        BSD-2-Clause AND MIT
Group:          System Environment/Daemons

%description module-brotli
ngx_brotli dynamic modules (ngx_http_brotli_filter_module and
ngx_http_brotli_static_module) for OpenResty. The brotli encoder is linked
statically. Each module has its own load_module snippet in conf/modules.d,
included by the default nginx.conf.
%endif


%if %{with zstd}
%package module-zstd
Version:        %{or_version}+0.1.1^git%{ngx_zstd_date}.%{ngx_zstd_short}
AutoReqProv:    yes
Requires:       openresty = %{or_evr}

Summary:        Zstandard filter and static dynamic modules for OpenResty
License:        BSD-2-Clause
Group:          System Environment/Daemons

%description module-zstd
zstd-nginx-module dynamic modules (ngx_http_zstd_filter_module and
ngx_http_zstd_static_module) for OpenResty, linked against the system
libzstd. Each module has its own load_module snippet in conf/modules.d,
included by the default nginx.conf.
%endif


%if %{with njs}
%package module-njs
Version:        %{or_version}+%{njs_version}
AutoReqProv:    yes
Requires:       openresty = %{or_evr}
Provides:       bundled(quickjs) = %{quickjs_version}^git%{quickjs_date}.%{quickjs_short}

Summary:        NGINX JavaScript (njs) http and stream dynamic modules for OpenResty
License:        BSD-2-Clause AND MIT
Group:          System Environment/Daemons

%description module-njs
njs dynamic modules (ngx_http_js_module and ngx_stream_js_module) for
OpenResty, built with the QuickJS engine (js_engine qjs), which is linked
statically. Each module has its own load_module snippet in conf/modules.d,
included by the default nginx.conf.
%endif


%if %{with xslt}
%package module-xslt
Version:        %{or_version}
AutoReqProv:    yes
Requires:       openresty = %{or_evr}

Summary:        XSLT filter (ngx_http_xslt_filter_module) dynamic module for OpenResty
License:        BSD-2-Clause
Group:          System Environment/Daemons

%description module-xslt
The nginx ngx_http_xslt_filter_module as a dynamic module for OpenResty
(transforms XML responses with XSLT stylesheets), linked dynamically against
libxml2 and libxslt. Load snippet in conf/modules.d.
%endif


%if %{with image_filter}
%package module-image-filter
Version:        %{or_version}
AutoReqProv:    yes
Requires:       openresty = %{or_evr}

Summary:        Image filter (ngx_http_image_filter_module) dynamic module for OpenResty
License:        BSD-2-Clause
Group:          System Environment/Daemons

%description module-image-filter
The nginx ngx_http_image_filter_module as a dynamic module for OpenResty
(transforms JPEG, GIF, PNG and WebP images), linked dynamically against libgd.
Load snippet in conf/modules.d.
%endif


%if %{with perl}
%package module-perl
Version:        %{or_version}
# main package sets AutoReqProv: no; libperl and the perl(...) deps come from here
AutoReqProv:    yes
Requires:       openresty = %{or_evr}
# nginx.so is XS code bound to the perl ABI it was built with
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

Summary:        Embedded Perl (ngx_http_perl_module) dynamic module for OpenResty
License:        BSD-2-Clause
Group:          System Environment/Daemons

%description module-perl
The nginx ngx_http_perl_module as a dynamic module for OpenResty, with its Perl
part (nginx.pm and the XS library) in conf-relative directory nginx/perl, which
is the compiled-in default Perl module path. Load snippet in conf/modules.d.
%endif


%if %{with geoip2}
%package module-geoip2
Version:        %{or_version}+%{ngx_geoip2_version}^git%{ngx_geoip2_date}.%{ngx_geoip2_short}
AutoReqProv:    yes
Requires:       openresty = %{or_evr}

Summary:        GeoIP2 (MaxMind DB) http and stream dynamic modules for OpenResty
License:        BSD-2-Clause
Group:          System Environment/Daemons

%description module-geoip2
ngx_http_geoip2_module and ngx_stream_geoip2_module for OpenResty, linked
dynamically against libmaxminddb. No MaxMind database is included: provide your
own .mmdb file. Each module has its own load_module snippet in conf/modules.d,
included by the default nginx.conf.
%endif


%prep
%setup -q -n "openresty-%{or_version}"

# conf/nginx.conf: include modules.d/*.conf (main context) and conf.d/*.conf (http context)
%{__patch} -p1 --fuzz=0 -d bundle/nginx-[0-9]*/ < %{PATCH0}

# third-party dynamic modules; compiled at the end of %build in a copy of the nginx tree
%if %{with brotli}
tar -xzf %{SOURCE10}
tar -xzf %{SOURCE11}
# GitHub archives do not contain git submodules: put brotli where ngx_brotli expects it
mv ngx_brotli-%{ngx_brotli_commit} ngx_brotli
rm -rf ngx_brotli/deps/brotli
mv brotli-%{brotli_version} ngx_brotli/deps/brotli
test -f ngx_brotli/deps/brotli/c/include/brotli/encode.h
%endif

%if %{with zstd}
tar -xzf %{SOURCE12}
mv zstd-nginx-module-%{ngx_zstd_commit} zstd-nginx-module
test -f zstd-nginx-module/config
%endif

%if %{with njs}
tar -xzf %{SOURCE13}
tar -xzf %{SOURCE14}
mv quickjs-%{quickjs_commit} quickjs
# njs configure runs the compiler as one word, but OpenResty sets it to "ccache gcc"
%{__patch} -p1 --fuzz=0 -d njs-%{njs_version} < %{PATCH13}
test -f njs-%{njs_version}/nginx/config
test -f quickjs/quickjs.h
%endif

%if %{with geoip2}
tar -xzf %{SOURCE15}
mv ngx_http_geoip2_module-%{ngx_geoip2_commit} ngx_http_geoip2_module
test -f ngx_http_geoip2_module/config
%endif


%build
./configure \
    --prefix="%{orprefix}" \
    --with-cc='ccache gcc -fdiagnostics-color=always' \
    --with-cc-opt="-DNGX_LUA_ABORT_AT_PANIC -I%{zlib_prefix}/include -I%{pcre_prefix}/include -I%{openssl_prefix}/include" \
    --with-ld-opt="-L%{zlib_prefix}/lib -L%{pcre_prefix}/lib -L%{openssl_prefix}/lib -Wl,-rpath,%{zlib_prefix}/lib:%{pcre_prefix}/lib:%{openssl_prefix}/lib" \
    --with-pcre-jit \
    --without-http_rds_json_module \
    --without-http_rds_csv_module \
    --without-lua_rds_parser \
    --with-stream \
    --with-stream_ssl_module \
    --with-stream_ssl_preread_module \
    --with-http_v2_module \
    --with-http_v3_module \
    --without-mail_pop3_module \
    --without-mail_imap_module \
    --without-mail_smtp_module \
    --with-http_stub_status_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_secure_link_module \
    --with-http_random_index_module \
    --with-http_gzip_static_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_slice_module \
    --with-threads \
%if %{with file_aio}
    --with-file-aio \
%endif
    --with-compat \
    --with-luajit-xcflags='-DLUAJIT_NUMMODE=2 -DLUAJIT_ENABLE_LUA52COMPAT' \
    -j`nproc`

make -j`nproc`

# ---- dynamic modules (brotli, zstd): begin ----
# Each enabled module adds its --add-dynamic-module to MOD_ARGS (and prepares its
# own libraries); the shell then builds all of them only if there are any.
# Built in a COPY of the nginx tree, with the configure arguments of the nginx
# binary just built, so they are binary compatible and the tree that
# `make install` uses stays untouched.
TOP=$(pwd)
MOD_ARGS=""
MOD_CC_OPT=""   # extra -I flags a module needs, appended to --with-cc-opt
MOD_LD_OPT=""   # extra -L flags a module needs, appended to --with-ld-opt

%if %{with brotli}
MOD_ARGS="$MOD_ARGS --add-dynamic-module=$TOP/ngx_brotli"
(
    cd ngx_brotli/deps/brotli
    mkdir -p out
    cd out
    cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DCMAKE_C_FLAGS="%{brotli_cflags}" \
        -DCMAKE_INSTALL_PREFIX=./installed ..
    cmake --build . --config Release --target brotlienc -j`nproc`
)
%endif

%if %{with zstd}
MOD_ARGS="$MOD_ARGS --add-dynamic-module=$TOP/zstd-nginx-module"
%endif

%if %{with njs}
MOD_ARGS="$MOD_ARGS --add-dynamic-module=$TOP/njs-%{njs_version}/nginx"
# njs finds quickjs.h and libquickjs.a through the compiler and linker flags
MOD_CC_OPT="$MOD_CC_OPT -I$TOP/quickjs"
MOD_LD_OPT="$MOD_LD_OPT -L$TOP/quickjs"
(
    cd quickjs
    CFLAGS="%{quickjs_cflags}" make libquickjs.a -j`nproc`
)
%endif

%if %{with xslt}
MOD_ARGS="$MOD_ARGS --with-http_xslt_module=dynamic"
%endif

%if %{with image_filter}
MOD_ARGS="$MOD_ARGS --with-http_image_filter_module=dynamic"
%endif

%if %{with perl}
# built-in nginx module, built dynamic by the same single configure run; the
# Perl part is looked up in the directory given by --with-perl_modules_path
MOD_ARGS="$MOD_ARGS --with-http_perl_module=dynamic --with-perl_modules_path=%{orprefix}/nginx/perl"
%endif

%if %{with geoip2}
MOD_ARGS="$MOD_ARGS --add-dynamic-module=$TOP/ngx_http_geoip2_module"
%endif

if [ -n "$MOD_ARGS" ]; then
    # exactly one numeric nginx dir expected (build/ also holds nginx-no_pool.patch)
    set -- "$TOP"/build/nginx-[0-9]*
    if [ $# -ne 1 ] || [ ! -x "$1/objs/nginx" ]; then
        echo "ERROR: expected exactly one built nginx dir in $TOP/build, got: $*" >&2
        ls -la "$TOP/build" >&2
        exit 1
    fi
    NGX_SRC=$1
    LJ="$TOP/build/luajit-root%{orprefix}/luajit"

    LD_LIBRARY_PATH="$LJ/lib:${LD_LIBRARY_PATH:-}" "$NGX_SRC/objs/nginx" -V > "$TOP/nginx-V.txt" 2>&1 \
        || { cat "$TOP/nginx-V.txt" >&2; exit 1; }

    NGX_ARGS=$(sed -n 's/^configure arguments: //p' "$TOP/nginx-V.txt")
    if [ -z "$NGX_ARGS" ]; then
        echo "ERROR: no 'configure arguments' in nginx -V:" >&2
        cat "$TOP/nginx-V.txt" >&2
        exit 1
    fi
    # the colour flag breaks the configure scripts of some modules (njs); drop it
    NGX_ARGS=$(printf '%s\n' "$NGX_ARGS" | sed -E "s| -fdiagnostics-color=always||g")

    # per-module extra flags go INSIDE the quoted --with-cc-opt / --with-ld-opt values
    if [ -n "$MOD_CC_OPT" ]; then
        NGX_ARGS=$(printf '%s\n' "$NGX_ARGS" | sed -E "s|(--with-cc-opt='[^']*)|\1$MOD_CC_OPT|")
    fi
    if [ -n "$MOD_LD_OPT" ]; then
        NGX_ARGS=$(printf '%s\n' "$NGX_ARGS" | sed -E "s|(--with-ld-opt='[^']*)|\1$MOD_LD_OPT|")
    fi

    # the name must not match nginx-[0-9]*; relative --add-module=../... paths still resolve
    rm -rf "$TOP/build/_modules-nginx"
    cp -a "$NGX_SRC" "$TOP/build/_modules-nginx"

    export LUAJIT_INC="$LJ/include/luajit-2.1"
    export LUAJIT_LIB="$LJ/lib"
    test -f "$LUAJIT_INC/lua.h" || { echo "ERROR: no $LUAJIT_INC/lua.h" >&2; exit 1; }

    (
        cd "$TOP/build/_modules-nginx"
        eval ./configure $NGX_ARGS $MOD_ARGS
        # make -j`nproc` modules
        make -j`nproc` modules LINK='$(CC) -Wl,--as-needed'
    )
fi
# ---- dynamic modules (brotli, zstd): end ----


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# snippet directories referenced by nginx.conf (owned via the conf/* glob in %files)
mkdir -p %{buildroot}%{orprefix}/nginx/conf/modules.d
mkdir -p %{buildroot}%{orprefix}/nginx/conf/conf.d

rm -rf %{buildroot}%{orprefix}/luajit/share/man
rm -rf %{buildroot}%{orprefix}/luajit/lib/libluajit-5.1.a

mkdir -p %{buildroot}/usr/bin
ln -sf %{orprefix}/bin/resty %{buildroot}/usr/bin/
ln -sf %{orprefix}/bin/restydoc %{buildroot}/usr/bin/
ln -sf %{orprefix}/bin/opm %{buildroot}/usr/bin/
ln -sf %{orprefix}/nginx/sbin/nginx %{buildroot}/usr/bin/%{name}

%if 0%{?use_systemd}

mkdir -p %{buildroot}%{_unitdir}
%{__install} -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/

%else

mkdir -p %{buildroot}/etc/init.d
%{__install} -p -m 0755 %{SOURCE2} %{buildroot}/etc/init.d/%{name}

%endif

# ---- dynamic modules (brotli, zstd): install ----
TOP=$(pwd)
MODDIR=%{buildroot}%{orprefix}/nginx/modules
CONFDIR=%{buildroot}%{orprefix}/nginx/conf/modules.d

mkdir -p "$MODDIR" "$CONFDIR"

# check-stage fragments (build-time only, not packaged): each module adds the directives
# that prove it is usable, into the context(s) it needs. Every file is spliced into
# ONE test nginx.conf, so name it after the module and keep it free of ports/files:
#   main/   root level: root directives and module-own contexts (rtmp { ... })
#   http/   inside http { }
#   stream/ inside stream { }
CHK="$TOP/check.d"
mkdir -p "$CHK/main" "$CHK/http" "$CHK/stream"

# One snippet per module, included by nginx.conf in name order. Of two modules of
# the same kind the one loaded LATER wins: zstd among filters (45 < 55), brotli
# among static modules (45 < 55). A precompressed file served by a static module
# beats every filter (they skip responses that already have a Content-Encoding).
%if %{with brotli}
for m in ngx_http_brotli_filter ngx_http_brotli_static; do
    %{__install} -m 0755 "$TOP/build/_modules-nginx/objs/${m}_module.so" "$MODDIR"/
done
cat > "$CONFDIR"/45-brotli-filter.conf <<'EOF'
load_module modules/ngx_http_brotli_filter_module.so;
EOF
cat > "$CONFDIR"/55-brotli-static.conf <<'EOF'
load_module modules/ngx_http_brotli_static_module.so;
EOF
cat > "$CHK"/http/brotli.conf <<'EOF'
brotli on;
brotli_static on;
EOF
%{__install} -Dm 0644 ngx_brotli/LICENSE %{buildroot}%{_licensedir}/%{name}-module-brotli/LICENSE.ngx_brotli
%{__install} -Dm 0644 ngx_brotli/deps/brotli/LICENSE %{buildroot}%{_licensedir}/%{name}-module-brotli/LICENSE.brotli
%endif

%if %{with zstd}
for m in ngx_http_zstd_filter ngx_http_zstd_static; do
    %{__install} -m 0755 "$TOP/build/_modules-nginx/objs/${m}_module.so" "$MODDIR"/
done
cat > "$CONFDIR"/45-zstd-static.conf <<'EOF'
load_module modules/ngx_http_zstd_static_module.so;
EOF
cat > "$CONFDIR"/55-zstd-filter.conf <<'EOF'
load_module modules/ngx_http_zstd_filter_module.so;
EOF
cat > "$CHK"/http/zstd.conf <<'EOF'
zstd on;
zstd_static on;
EOF
%{__install} -Dm 0644 zstd-nginx-module/LICENSE %{buildroot}%{_licensedir}/%{name}-module-zstd/LICENSE.zstd-nginx-module
%endif

%if %{with njs}
for m in ngx_http_js ngx_stream_js; do
    %{__install} -m 0755 "$TOP/build/_modules-nginx/objs/${m}_module.so" "$MODDIR"/
done
cat > "$CONFDIR"/50-njs-http.conf <<'EOF'
load_module modules/ngx_http_js_module.so;
EOF
cat > "$CONFDIR"/50-njs-stream.conf <<'EOF'
load_module modules/ngx_stream_js_module.so;
EOF
cat > "$CHK"/http/njs.conf <<'EOF'
js_engine qjs;
EOF
cat > "$CHK"/stream/njs.conf <<'EOF'
js_engine qjs;
EOF
%{__install} -Dm 0644 njs-%{njs_version}/LICENSE %{buildroot}%{_licensedir}/%{name}-module-njs/LICENSE.njs
%{__install} -Dm 0644 quickjs/LICENSE %{buildroot}%{_licensedir}/%{name}-module-njs/LICENSE.quickjs
%endif

%if %{with xslt}
%{__install} -m 0755 "$TOP/build/_modules-nginx/objs/ngx_http_xslt_filter_module.so" "$MODDIR"/
cat > "$CONFDIR"/60-xslt.conf <<'EOF'
load_module modules/ngx_http_xslt_filter_module.so;
EOF
# xslt_stylesheet is location-only and needs a file; xslt_types is accepted in http
cat > "$CHK"/http/xslt.conf <<'EOF'
xslt_types text/xml;
EOF
%{__install} -Dm 0644 bundle/nginx-[0-9]*/LICENSE %{buildroot}%{_licensedir}/%{name}-module-xslt/LICENSE.nginx
%endif

%if %{with image_filter}
%{__install} -m 0755 "$TOP/build/_modules-nginx/objs/ngx_http_image_filter_module.so" "$MODDIR"/
cat > "$CONFDIR"/50-image-filter.conf <<'EOF'
load_module modules/ngx_http_image_filter_module.so;
EOF
# image_filter itself is location-only; the buffer directive is accepted in http
cat > "$CHK"/http/image-filter.conf <<'EOF'
image_filter_buffer 2M;
EOF
%{__install} -Dm 0644 bundle/nginx-[0-9]*/LICENSE %{buildroot}%{_licensedir}/%{name}-module-image-filter/LICENSE.nginx
%endif

%if %{with perl}
PERLBLIB="$TOP/build/_modules-nginx/objs/src/http/modules/perl/blib"
PERLDIR=%{buildroot}%{orprefix}/nginx/perl
%{__install} -m 0755 "$TOP/build/_modules-nginx/objs/ngx_http_perl_module.so" "$MODDIR"/
# nginx.pm and the XS library must share one @INC directory (auto/nginx/ below it)
%{__install} -Dm 0644 "$PERLBLIB/lib/nginx.pm" "$PERLDIR/nginx.pm"
%{__install} -Dm 0755 "$PERLBLIB/arch/auto/nginx/nginx.so" "$PERLDIR/auto/nginx/nginx.so"
cat > "$CONFDIR"/50-perl.conf <<'EOF'
load_module modules/ngx_http_perl_module.so;
EOF
# check fragment: perl_set forces the interpreter to start, which loads nginx.pm
# and the XS library; the module path points into the buildroot for the check stage
cat > "$CHK"/http/perl.conf <<EOF
perl_modules %{buildroot}%{orprefix}/nginx/perl;
perl_set \$perl_check 'sub { return "ok"; }';
EOF
%{__install} -Dm 0644 bundle/nginx-[0-9]*/LICENSE %{buildroot}%{_licensedir}/%{name}-module-perl/LICENSE.nginx
%endif

%if %{with geoip2}
for m in ngx_http_geoip2 ngx_stream_geoip2; do
    %{__install} -m 0755 "$TOP/build/_modules-nginx/objs/${m}_module.so" "$MODDIR"/
done
cat > "$CONFDIR"/50-geoip2-http.conf <<'EOF'
load_module modules/ngx_http_geoip2_module.so;
EOF
cat > "$CONFDIR"/50-geoip2-stream.conf <<'EOF'
load_module modules/ngx_stream_geoip2_module.so;
EOF
# the geoip2 directive opens its database at parse time, so it cannot be used in the
# check; this one needs no file and proves the http module registered its directives
cat > "$CHK"/http/geoip2.conf <<'EOF'
geoip2_proxy_recursive off;
EOF
%{__install} -Dm 0644 ngx_http_geoip2_module/LICENSE %{buildroot}%{_licensedir}/%{name}-module-geoip2/LICENSE.geoip2
%endif

# to silence the check-rpath error
export QA_RPATHS=$[ 0x0002 ]


%check
# Load every installed module with the nginx binary of this build: a signature/ABI
# mismatch fails here with "is not binary compatible", then parse the directives each
# module contributed (check.d/, written in the install stage). load_module lines come from the
# installed snippets (name order = load order, as nginx.conf includes them), pointed
# at the freshly built .so files. No per-module code here.
set -- %{buildroot}%{orprefix}/nginx/conf/modules.d/*.conf
if [ -e "$1" ]; then
    TOP=$(pwd)
    CHK="$TOP/check.d"
    LOADS=$(cat "$@" | sed "s#load_module modules/#load_module $TOP/build/_modules-nginx/objs/#")
    set -- "$TOP"/build/nginx-[0-9]*
    NGX_SRC=$1
    LJ="$TOP/build/luajit-root%{orprefix}/luajit"
    T=$(mktemp -d)
    mkdir -p "$T/logs"
    emit() { for f in "$@"; do if [ -e "$f" ]; then cat "$f"; fi; done; }
    {
        printf '%s\n' "$LOADS"
        echo "pid $T/nginx.pid;"
        echo "error_log stderr;"
        echo "events {}"
        emit "$CHK"/main/*.conf
        echo "http {"
        echo "access_log off;"
        emit "$CHK"/http/*.conf
        echo "}"
        echo "stream {"
        emit "$CHK"/stream/*.conf
        echo "}"
    } > "$T/nginx.conf"
    LD_LIBRARY_PATH="$LJ/lib:${LD_LIBRARY_PATH:-}" "$NGX_SRC/objs/nginx" -t -p "$T/" -c "$T/nginx.conf"
    rm -rf "$T"
fi


%clean
rm -rf %{buildroot}


%post

%if 0%{?use_systemd}
%systemd_post openresty.service
%else
%if ! 0%{?suse_version}
/sbin/chkconfig --add %{name}
%endif
%endif


%preun
%if 0%{?use_systemd}
%systemd_preun openresty.service
%else
%if ! 0%{?suse_version}
if [ $1 = 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
%endif
%endif


%if 0%{?use_systemd}
%postun
%systemd_postun_with_restart openresty.service
%endif


%files
%defattr(-,root,root,-)

%dir %{orprefix}
%dir %{orprefix}/bin
%dir %{orprefix}/luajit
%dir %{orprefix}/lualib
%dir %{orprefix}/nginx
%dir %{orprefix}/nginx/html
%dir %{orprefix}/nginx/logs
%dir %{orprefix}/nginx/sbin
%if 0%{?use_systemd}
%{_unitdir}/%{name}.service
%else
/etc/init.d/%{name}
%endif
/usr/bin/%{name}
%{orprefix}/bin/openresty
%{orprefix}/site/lualib/
%{orprefix}/luajit/*
%{orprefix}/lualib/*
%{orprefix}/nginx/html/*
%{orprefix}/nginx/logs/
%{orprefix}/nginx/sbin/*
%config(noreplace) %{orprefix}/nginx/conf/*
# the module snippets belong to the module sub-packages
%exclude %{orprefix}/nginx/conf/modules.d/*.conf
%{orprefix}/COPYRIGHT


%files resty
%dir %{orprefix}/bin
%defattr(-,root,root,-)

/usr/bin/resty
%{orprefix}/bin/resty


%files doc
%defattr(-,root,root,-)

%dir %{orprefix}/pod
/usr/bin/restydoc
%{orprefix}/bin/restydoc
%{orprefix}/bin/restydoc-index
%{orprefix}/bin/md2pod.pl
%{orprefix}/bin/nginx-xml2pod
%{orprefix}/pod/*
%{orprefix}/resty.index


%files opm
%defattr(-,root,root,-)

/usr/bin/opm
%dir %{orprefix}/site
%dir %{orprefix}/site/pod
%dir %{orprefix}/site/manifest
%{orprefix}/bin/opm
%{orprefix}/site/manifest/
%{orprefix}/site/pod/


%if %{with brotli}
%files module-brotli
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%{orprefix}/nginx/modules/ngx_http_brotli_filter_module.so
%{orprefix}/nginx/modules/ngx_http_brotli_static_module.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/45-brotli-filter.conf
%config(noreplace) %{orprefix}/nginx/conf/modules.d/55-brotli-static.conf
%license %{_licensedir}/%{name}-module-brotli/*
%endif


%if %{with zstd}
%files module-zstd
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%{orprefix}/nginx/modules/ngx_http_zstd_filter_module.so
%{orprefix}/nginx/modules/ngx_http_zstd_static_module.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/45-zstd-static.conf
%config(noreplace) %{orprefix}/nginx/conf/modules.d/55-zstd-filter.conf
%license %{_licensedir}/%{name}-module-zstd/*
%endif


%if %{with njs}
%files module-njs
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%{orprefix}/nginx/modules/ngx_http_js_module.so
%{orprefix}/nginx/modules/ngx_stream_js_module.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/50-njs-http.conf
%config(noreplace) %{orprefix}/nginx/conf/modules.d/50-njs-stream.conf
%license %{_licensedir}/%{name}-module-njs/*
%endif


%if %{with xslt}
%files module-xslt
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%{orprefix}/nginx/modules/ngx_http_xslt_filter_module.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/60-xslt.conf
%license %{_licensedir}/%{name}-module-xslt/*
%endif


%if %{with image_filter}
%files module-image-filter
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%{orprefix}/nginx/modules/ngx_http_image_filter_module.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/50-image-filter.conf
%license %{_licensedir}/%{name}-module-image-filter/*
%endif


%if %{with perl}
%files module-perl
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%dir %{orprefix}/nginx/perl
%dir %{orprefix}/nginx/perl/auto
%dir %{orprefix}/nginx/perl/auto/nginx
%{orprefix}/nginx/modules/ngx_http_perl_module.so
%{orprefix}/nginx/perl/nginx.pm
%{orprefix}/nginx/perl/auto/nginx/nginx.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/50-perl.conf
%license %{_licensedir}/%{name}-module-perl/*
%endif


%if %{with geoip2}
%files module-geoip2
%defattr(-,root,root,-)
%dir %{orprefix}/nginx/modules
%dir %{orprefix}/nginx/conf/modules.d
%{orprefix}/nginx/modules/ngx_http_geoip2_module.so
%{orprefix}/nginx/modules/ngx_stream_geoip2_module.so
%config(noreplace) %{orprefix}/nginx/conf/modules.d/50-geoip2-http.conf
%config(noreplace) %{orprefix}/nginx/conf/modules.d/50-geoip2-stream.conf
%license %{_licensedir}/%{name}-module-geoip2/*
%endif


%changelog
* Sat Nov 14 2026 Ivan Shatsky <ivan@shatsky.net> 1.31.8.1-1
- nginx.conf: include modules.d/*.conf and conf.d/*.conf; create both directories.
- new sub-packages openresty-module-brotli and openresty-module-zstd (ngx_brotli
  and zstd-nginx-module as dynamic modules, built in the same build), one
  load_module snippet per module numbered 45/55: zstd wins among filters, brotli
  among static modules.
- module sub-packages are optional: rpmbuild --without brotli / --without zstd
  (both are built by default unless global --without modules option used).
- new sub-package openresty-module-njs (njs 1.0.2 with QuickJS, http and stream
  modules); the shared module build now passes per-module -I/-L flags and strips
  -fdiagnostics-color from the module configure arguments.
- module sub-packages carry Version <openresty>+<module version>
  and bundled() provides;
  OpenResty version in Requires/%setup comes from the or_version/or_evr macros.
- new sub-package openresty-module-xslt (ngx_http_xslt_filter_module built dynamic
  from the bundled nginx, linked against the system libxml2 and libxslt).
- new sub-package openresty-module-image-filter (ngx_http_image_filter_module
  built dynamic from the bundled nginx, linked against the system libgd).
- new sub-package openresty-module-perl (ngx_http_perl_module built dynamic from
  the bundled nginx; nginx.pm and its XS library in nginx/perl, the compiled-in
  module path).
- new sub-package openresty-module-geoip2 (ngx_http_geoip2_module 3.4 plus later
  commits, http and stream modules, linked against the system libmaxminddb).
* Mon Oct 26 2026 Yichun Zhang (agentzh) 1.31.8.1-1
- upgraded openresty to 1.31.8.1.
* Mon Aug 31 2026 Yichun Zhang (agentzh) 1.31.4.1-1
- upgraded openresty to 1.31.4.1.
* Thu Jun 4 2026 Yichun Zhang (agentzh) 1.31.1.1-1
- upgraded openresty to 1.31.1.1.
* Tue May 26 2026 Yichun Zhang (agentzh) 1.29.2.5-1
- upgraded openresty to 1.29.2.5.
* Fri May 15 2026 Yichun Zhang (agentzh) 1.29.2.4-1
- upgraded openresty to 1.29.2.4.
* Wed Mar 25 2026 Yichun Zhang (agentzh) 1.29.2.3-1
- upgraded openresty to 1.29.2.3.
* Thu Mar 19 2026 Yichun Zhang (agentzh) 1.29.2.2-1
- upgraded openresty to 1.29.2.2.
* Fri Feb 27 2026 Yichun Zhang (agentzh) 1.29.2.1-1
- upgraded openresty to 1.29.2.1.
* Mon Mar 31 2025 Yichun Zhang (agentzh) 1.27.1.2-1
- upgraded openresty to 1.27.1.2.
* Mon Aug 19 2024 Yichun Zhang (agentzh) 1.27.1.1-1
- upgraded openresty to 1.27.1.1.
* Tue Jul 9 2024 Yichun Zhang (agentzh) 1.25.3.2-1
- upgraded openresty to 1.25.3.2.
* Thu Jan 4 2024 Yichun Zhang (agentzh) 1.25.3.1-1
- upgraded openresty to 1.25.3.1.
* Thu Oct 26 2023 Yichun Zhang (agentzh) 1.21.4.3-1
- upgraded openresty to 1.21.4.3.
* Mon Jul 17 2023 Yichun Zhang (agentzh) 1.21.4.2-1
- upgraded openresty to 1.21.4.2.
* Tue May 17 2022 Yichun Zhang (agentzh) 1.21.4.1-1
- upgraded openresty to 1.21.4.1.
* Fri Aug 6 2021 Yichun Zhang (agentzh) 1.19.9.1-1
- upgraded openresty to 1.19.9.1.
* Mon May 31 2021 Yichun Zhang (agentzh) 1.19.3.2-1
- upgraded openresty to 1.19.3.2.
* Fri Nov 6 2020 Yichun Zhang (agentzh) 1.19.3.1-1
- upgraded openresty to 1.19.3.1.
* Mon Jul 13 2020 Yichun Zhang (agentzh) 1.17.8.2-1
- upgraded openresty to 1.17.8.2.
* Fri Jul 3 2020 Yichun Zhang (agentzh) 1.17.8.1-1
- upgraded openresty to 1.17.8.1.
* Thu Aug 29 2019 Yichun Zhang (agentzh) 1.15.8.2-1
- upgraded openresty to 1.15.8.2.
* Thu May 16 2019 Yichun Zhang (agentzh) 1.15.8.1-1
- upgraded openresty to 1.15.8.1.
* Mon May 14 2018 Yichun Zhang (agentzh) 1.13.6.2-1
- upgraded openresty to 1.13.6.2.
* Sun Nov 12 2017 Yichun Zhang (agentzh) 1.13.6.1-1
- upgraded openresty to 1.13.6.1.
* Thu Sep 21 2017 Yichun Zhang (agentzh) 1.11.2.5-2
- enabled -DNGX_LUA_ABORT_AT_PANIC by default.
* Thu Aug 17 2017 Yichun Zhang (agentzh) 1.11.2.5-1
- upgraded OpenResty to 1.11.2.5.
* Tue Jul 11 2017 Yichun Zhang (agentzh) 1.11.2.4-1
- upgraded OpenResty to 1.11.2.4.
* Sat May 27 2017 Yichun Zhang (agentzh) 1.11.2.3-14
- bugfix: the openresty-opm subpackage did not depend on openresty-doc and openresty-resty.
* Sat May 27 2017 Yichun Zhang (agentzh) 1.11.2.3-14
- centos 6 and opensuse do not have the groff-base package.
* Sat May 27 2017 Yichun Zhang (agentzh) 1.11.2.3-13
- openresty-doc now depends on groff-base.
* Thu May 25 2017 Yichun Zhang (agentzh) 1.11.2.3-12
- added missing groff/pod2txt/pod2man dependencies for openresty-doc.
* Thu May 25 2017 Yichun Zhang (agentzh) 1.11.2.3-11
- added missing perl dependencies for openresty-opm, openresty-resty, and openresty-doc.
* Sun May 21 2017 Yichun Zhang (agentzh) 1.11.2.3-10
- removed the geoip nginx module since GeoIP is not available everywhere.
* Fri Apr 21 2017 Yichun Zhang (agentzh)
- upgrade to the OpenResty 1.11.2.3 release: http://openresty.org/en/changelog-1011002.html
* Sat Dec 24 2016 Yichun Zhang
- init script: explicity specify the runlevels 345.
* Wed Dec 14 2016 Yichun Zhang
- opm missing runtime dependencies curl, tar, and gzip.
- enabled http_geoip_module by default.
* Fri Nov 25 2016 Yichun Zhang
- opm missing runtime dependency perl(Digest::MD5)
* Thu Nov 17 2016 Yichun Zhang
- upgraded OpenResty to 1.11.2.2.
* Fri Aug 26 2016 Yichun Zhang
- use dual number mode in our luajit builds which should usually
be faster for web application use cases.
* Wed Aug 24 2016 Yichun Zhang
- bump OpenResty version to 1.11.2.1.
* Tue Aug 23 2016 zxcvbn4038
- use external packages openresty-zlib and openresty-pcre through dynamic linking.
* Thu Jul 14 2016 Yichun Zhang
- enabled more nginx standard modules as well as threads and file aio.
* Sun Jul 10 2016 makerpm
- initial build for OpenResty 1.9.15.1.
