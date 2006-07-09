#
# Conditional build:
%bcond_with	tests		# build with tests
%bcond_without	tests		# build without tests
#
Summary:	The flowd NetFlow collector daemon
Name:		flowd
Version:	0.9
Release:	1
License:	BSD
Group:		Applications/Networking
URL:		http://www.mindrot.org/flowd.html
Source0:	http://www.mindrot.org/files/flowd/%{name}-%{version}.tar.gz
# Source0-md5:	442917bb3c66a81786e9ab1d40006122
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%package perl
Summary:	Perl API to access flowd logfiles
Group:		Applications/Networking
Requires:	perl

%package python
Summary:	Python API to access flowd logfiles
Group:		Applications/Networking
Requires:	python

%package tools
Summary:	Collection of example flowd tools
Group:		Applications/Networking

%package devel
Summary:	C API to access flowd logfiles
Group:		Applications/Networking

%description
This is flowd, a NetFlow collector daemon intended to be small, fast
and secure.

It features some basic filtering to limit or tag the flows that are
recorded and is privilege separated, to limit security exposure from
bugs in flowd itself.

%description perl
This is a Perl API to the binary flowd network flow log format and an
example reader application

%description python
This is a Python API to the binary flowd network flow log format and
an example reader application

%description tools
A collection of tools for use with flowd

%description devel
This is a C API to the binary flowd network flow log format.

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
cd Flowd-perl; 
%{__make} pure_install \
	DESTDIR=$RPM_BUILD_ROOT
cd ..

# Python module
./setup.py install --optimize 1 --root=$RPM_BUILD_ROOT 

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%{_sbindir}/groupadd -r _flowd 2>/dev/null || :
%{_sbindir}/useradd -d /var/empty -s /bin/false -g _flowd -M -r _flowd \
	2>/dev/null || :

%post
/sbin/chkconfig --add flowd

%postun
%service flowd condrestart > /dev/null 2>&1 || :

%preun
if [ "$1" = 0 ]
then
	%service flowd stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del flowd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog LICENSE README TODO
#%%dir %%attr(111,root,root) %{_var}/empty
%attr(600,root,root) %config(noreplace) %{_sysconfdir}/flowd.conf
%attr(644,root,root) %{_mandir}/man5/flowd.conf.5*
%attr(644,root,root) %{_mandir}/man8/flowd.8*
%attr(644,root,root) %{_mandir}/man8/flowd-reader.8*
%attr(755,root,root) %{_bindir}/flowd-reader
%attr(755,root,root) %config /etc/rc.d/init.d/flowd
%attr(755,root,root) %{_sbindir}/flowd

%files perl 
%defattr(644,root,root,755)
#%%doc reader.pl
%{perl_vendorarch}/Flowd.pm
%{perl_vendorarch}/auto/Flowd/Flowd.bs
%{perl_vendorarch}/auto/Flowd/Flowd.so
%{_mandir}/man3/*

%files python 
%defattr(644,root,root,755)
%doc reader.py

%files tools
%defattr(644,root,root,755)
%doc tools/*

%files devel
%defattr(644,root,root,755)
%dir %attr(755,root,root) %{_includedir}/flowd
%attr(644,root,root) %{_includedir}/flowd/*
%attr(644,root,root) %{_libdir}/libflowd.a
