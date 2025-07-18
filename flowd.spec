#
# Conditional build:
%bcond_without	tests		# build without tests
#
Summary:	The flowd NetFlow collector daemon
Summary(pl.UTF-8):	flowd - demon zbierania danych NetFlow
Name:		flowd
Version:	0.9.1
Release:	19
License:	BSD
Group:		Applications/Networking
Source0:	http://www.mindrot.org/files/flowd/%{name}-%{version}.tar.gz
# Source0-md5:	a3d0512b5e6d9c7d9e749d9894376ea4
Patch0:		%{name}-username.patch
Patch1:		format-error.patch
URL:		http://www.mindrot.org/flowd.html
BuildRequires:	byacc
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	python-devel
BuildRequires:	python-modules
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.710
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(flowd)
Provides:	user(flowd)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is flowd, a NetFlow collector daemon intended to be small, fast
and secure.

It features some basic filtering to limit or tag the flows that are
recorded and is privilege separated, to limit security exposure from
bugs in flowd itself.

%description -l pl.UTF-8
Ten pakiet zawiera program flowd - demona zbierającego dane NetFlow,
mającego być małym, szybkim i bezpiecznym.

Obsługuje podstawowe filtrowanie w celu ograniczania lub znakowania
zapisywanych przepływów, ma rozdzielenie uprawnień w celu ograniczenia
wpływu własnych błedów na bezpieczeństwo.

%package -n perl-Flowd
Summary:	Perl API to access flowd logfiles
Summary(pl.UTF-8):	Perlowe API do dostępu do plików logów flowd
Group:		Development/Languages/Perl
Obsoletes:	flowd-perl

%description -n perl-Flowd
This is a Perl API to the binary flowd network flow log format and an
example reader application.

%description -n perl-Flowd -l pl.UTF-8
Ten pakiet zawiera API Perla dla binarnego formatu plików logów
przepływów sieciowych flowd oraz przykładowy program czytający.

%package -n python-flowd
Summary:	Python API to access flowd logfiles
Summary(pl.UTF-8):	Pythonowe API do dostępu do plików logów flowd
Group:		Applications/Networking
Obsoletes:	flowd-python

%description -n python-flowd
This is a Python API to the binary flowd network flow log format and
an example reader application.

%description -n python-flowd -l pl.UTF-8
Ten pakiet zawiera API Pythona dla binarnego formatu plików logów
przepływów sieciowych flowd oraz przykładowy program czytający.

%package tools
Summary:	Collection of example flowd tools
Summary(pl.UTF-8):	Zbiór przykładowych narzędzi dla flowd
Group:		Applications/Networking

%description tools
A collection of tools for use with flowd.

%description tools -l pl.UTF-8
Zbiór narzędzi do używania z flowd.

%package devel
Summary:	C API to access flowd logfiles
Summary(pl.UTF-8):	API C do dostępu do plików logów flowd
Group:		Development/Libraries

%description devel
This is a C API to the binary flowd network flow log format.

%description devel -l pl.UTF-8
Ten pakiet zawiera API C dla binarnego formatu plików logów przepływów
sieciowych flowd.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%build
%configure
%{__make}

%py_build

cd Flowd-perl
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make}
%{?with_tests:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Misc stuff
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -p flowd.init $RPM_BUILD_ROOT/etc/rc.d/init.d/flowd

# Perl module
%{__make} -C Flowd-perl pure_install \
	DESTDIR=$RPM_BUILD_ROOT

rm $RPM_BUILD_ROOT%{perl_vendorarch}/auto/Flowd/.packlist

# Python module
%py_install

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 198 flowd
%useradd -u 198 -d /usr/share/empty -s /bin/false -c "flowd user" -g flowd flowd

%post
/sbin/chkconfig --add flowd
%service flowd restart "flowd daemon"

%preun
if [ "$1" = "0" ]; then
	%service flowd stop
	/sbin/chkconfig --del flowd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove flowd
	%groupremove flowd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog LICENSE README TODO
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/flowd.conf
%attr(754,root,root) /etc/rc.d/init.d/flowd
%attr(755,root,root) %{_bindir}/flowd-reader
%attr(755,root,root) %{_sbindir}/flowd
%{_mandir}/man5/flowd.conf.5*
%{_mandir}/man8/flowd.8*
%{_mandir}/man8/flowd-reader.8*

%files -n perl-Flowd
%defattr(644,root,root,755)
%doc reader.pl
%{perl_vendorarch}/Flowd.pm
%dir %{perl_vendorarch}/auto/Flowd
%attr(755,root,root) %{perl_vendorarch}/auto/Flowd/Flowd.so
%{_mandir}/man3/Flowd.3pm*

%files -n python-flowd
%defattr(644,root,root,755)
%doc reader.py
%attr(755,root,root) %{py_sitedir}/flowd.so
%if "%{py_ver}" > "2.4"
%{py_sitedir}/flowd-*.egg-info
%endif

%files tools
%defattr(644,root,root,755)
%doc tools/*

%files devel
%defattr(644,root,root,755)
%{_includedir}/flowd
%{_libdir}/libflowd.a
