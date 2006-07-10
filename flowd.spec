#
# Conditional build:
%bcond_without	tests		# build without tests
#
%include	/usr/lib/rpm/macros.perl
Summary:	The flowd NetFlow collector daemon
Summary(pl):	flowd - demon zbierania danych NetFlow
Name:		flowd
Version:	0.9
Release:	1
License:	BSD
Group:		Applications/Networking
Source0:	http://www.mindrot.org/files/flowd/%{name}-%{version}.tar.gz
# Source0-md5:	442917bb3c66a81786e9ab1d40006122
URL:		http://www.mindrot.org/flowd.html
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	rc-scripts
Provides:	group(_flowd)
Provides:	user(_flowd)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is flowd, a NetFlow collector daemon intended to be small, fast
and secure.

It features some basic filtering to limit or tag the flows that are
recorded and is privilege separated, to limit security exposure from
bugs in flowd itself.

%description -l pl
Ten pakiet zawiera program flowd - demona zbieraj±cego dane NetFlow,
maj±cego byæ ma³ym, szybkim i bezpiecznym.

Obs³uguje podstawowe filtrowanie w celu ograniczania lub znakowania
zapisywanych przep³ywów, ma rozdzielenie uprawnieñ w celu ograniczenia
wp³ywu w³asnych b³edów na bezpieczeñstwo.

%package perl
Summary:	Perl API to access flowd logfiles
Summary(pl):	Perlowe API do dostêpu do plików logów flowd
Group:		Development/Languages/Perl

%description perl
This is a Perl API to the binary flowd network flow log format and an
example reader application.

%description perl -l pl
Ten pakiet zawiera API Perla dla binarnego formatu plików logów
przep³ywów sieciowych flowd oraz przyk³adowy program czytaj±cy.

%package python
Summary:	Python API to access flowd logfiles
Summary(pl):	Pythonowe API do dostêpu do plików logów flowd
Group:		Applications/Networking
Requires:	python

%description python
This is a Python API to the binary flowd network flow log format and
an example reader application.

%description python -l pl
Ten pakiet zawiera API Pythona dla binarnego formatu plików logów
przep³ywów sieciowych flowd oraz przyk³adowy program czytaj±cy.

%package tools
Summary:	Collection of example flowd tools
Summary(pl):	Zbiór przyk³adowych narzêdzi dla flowd
Group:		Applications/Networking

%description tools
A collection of tools for use with flowd.

%description tools -l pl
Zbiór narzêdzi do u¿ywania z flowd.

%package devel
Summary:	C API to access flowd logfiles
Summary(pl):	API C do dostêpu do plików logów flowd
Group:		Development/Libraries

%description devel
This is a C API to the binary flowd network flow log format.

%description devel -l pl
Ten pakiet zawiera API C dla binarnego formatu plików logów przep³ywów
sieciowych flowd.

%prep
%setup -q

%build
%configure
#	--enable-gcc-warnings \

%{__make}

cd Flowd-perl 
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make} 
%{?with_tests:%{__make} test}

#python setup.py install --root=$RPM_BUILD_ROOT --optimize=2

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# Misc stuff
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install flowd.init $RPM_BUILD_ROOT/etc/rc.d/init.d/flowd

# Perl module
%{__make} -C Flowd-perl pure_install \
	DESTDIR=$RPM_BUILD_ROOT

# Python module
./setup.py install --optimize 1 --root=$RPM_BUILD_ROOT 

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g XXX _flowd
%useradd -u XXX -d /usr/share/empty -s /bin/false -c "flowd user" -g _flowd _flowd

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
	%userremove _flowd
	%groupremove _flowd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog LICENSE README TODO
#%%dir %%attr(111,root,root) %{_var}/empty
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/flowd.conf
%attr(754,root,root) /etc/rc.d/init.d/flowd
%attr(755,root,root) %{_bindir}/flowd-reader
%attr(755,root,root) %{_sbindir}/flowd
%{_mandir}/man5/flowd.conf.5*
%{_mandir}/man8/flowd.8*
%{_mandir}/man8/flowd-reader.8*

%files perl 
%defattr(644,root,root,755)
#%%doc reader.pl
%{perl_vendorarch}/Flowd.pm
%dir %{perl_vendorarch}/auto/Flowd
%{perl_vendorarch}/auto/Flowd/Flowd.bs
%attr(755,root,root) %{perl_vendorarch}/auto/Flowd/Flowd.so
%{_mandir}/man3/*

%files python 
%defattr(644,root,root,755)
%doc reader.py

%files tools
%defattr(644,root,root,755)
%doc tools/*

%files devel
%defattr(644,root,root,755)
%{_includedir}/flowd
%{_libdir}/libflowd.a
