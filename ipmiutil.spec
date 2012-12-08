%define name    ipmiutil
%define version	2.7.1
%define release %mkrel 3

Name:       %name
Version:    %version
Release:    %release
Summary:    A package that includes various IPMI server management utilities
License:    BSD
Group:      System/Kernel and hardware
Url:	    http://ipmiutil.sourceforge.net/
Source:     http://optusnet.dl.sourceforge.net/sourceforge/ipmiutil/%{name}-%{version}.tar.gz
Patch:      ipmiutil-2.7.1-fix-format-errors.patch
BuildRequires:  freeipmi-devel
BuildRequires:  openssl-devel
ExcludeArch:    ppc %mips %arm
BuildRoot:      %{_tmppath}/%{name}-%{version}

%description
The ipmiutil component package provides utilities to view the SEL (showsel), 
perform a hardware reset (hwreset), and set up the Platform Event Filter :q!

entry to allow BMC LAN alerts from OS Critical Stop messages (pefconfig).  
It requires an IPMI driver (ipmidrvr) package in order to talk to the 
BMC/firmware interface.
An IPMI driver can be provided by either the Intel IPMI driver (/dev/imb) 
or the valinux IPMI driver (/dev/ipmikcs).

%prep
%setup -q
%patch -p 1

%build
%configure2_5x --enable-gpl --disable-nongpl
make

%install
rm -rf %{buildroot}
%makeinstall_std
rm -f %{buildroot}%{_datadir}/%{name}/{README,COPYING}

%clean
rm -rf %{buildroot}

%post
# after install
tmpsel=/tmp/pefcfg.tmp

# Assumes that the kernel patches are already in place.

# Make sure that the panic timeout is set to some reasonable value
PANIC_MODE=5
PANIC_FILE=/proc/sys/kernel/panic
PANIC_VALUE=`cat $PANIC_FILE`

# assume that if $pval is set, that someone has already configured lilo.conf
if [ "$PANIC_VALUE" = "0" ]
then
   # Panic timeout is not set, set timeout to $pnew
   echo "$PANIC_MODE" > $PANIC_FILE
   echo "kernel.panic=$PANIC_MODE" >> /etc/sysctl.conf
fi

# Set up the PEF entry to send the BMC LAN Alert for this event.
%{_sbindir}/pefconfig >$tmpsel 2>&1

%files
%defattr(-,root,root)
%doc README COPYING AUTHORS NEWS TODO INSTALL
%{_sbindir}/*
%{_datadir}/%{name}
%{_mandir}/man8/*
%config(noreplace) %{_sysconfdir}/cron.daily/checksel
%{_initrddir}/ipmi_port
%{_initrddir}/ipmiutil_asy
%{_initrddir}/ipmiutil_wdt
%{_initrddir}/ipmiutil_evt


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 2.7.1-2mdv2011.0
+ Revision: 665517
- mass rebuild

* Mon Dec 27 2010 Guillaume Rousse <guillomovitch@mandriva.org> 2.7.1-1mdv2011.0
+ Revision: 625380
- new version

* Sun Aug 08 2010 Guillaume Rousse <guillomovitch@mandriva.org> 2.6.8-1mdv2011.0
+ Revision: 567754
- new version

* Wed Apr 28 2010 Funda Wang <fwang@mandriva.org> 2.6.3-1mdv2010.1
+ Revision: 539920
- New version 2.6.3
- patch against openssl is not needed

* Wed Apr 21 2010 Funda Wang <fwang@mandriva.org> 2.6.2-1mdv2010.1
+ Revision: 537364
- new version 2.6.2
- build with openssl 1.0
- rebuild
- rebuild

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 2.4.1-4mdv2010.1
+ Revision: 511578
- rebuilt against openssl-0.9.8m

* Fri Sep 25 2009 Olivier Blin <oblin@mandriva.com> 2.4.1-3mdv2010.0
+ Revision: 449107
- do not build on mips & arm (from Arnaud Patard)

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 2.4.1-2mdv2010.0
+ Revision: 425370
- rebuild

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - new version

* Thu Apr 09 2009 Funda Wang <fwang@mandriva.org> 1.9.2-2mdv2009.1
+ Revision: 365416
- fix str fmt

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 1.9.2-2mdv2009.0
+ Revision: 221636
- rebuild

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 1.9.2-1mdv2008.1
+ Revision: 127110
- kill re-definition of %%buildroot on Pixel's request


* Wed Mar 14 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.9.2-1mdv2007.1
+ Revision: 143850
- fix build dependencies
- new version

* Sat Dec 31 2005 Mandriva Linux Team <http://www.mandrivaexpert.com/> 1.6.4-2mdk
- Rebuild

* Tue Jun 14 2005 Erwan Velu <velu@seanodes.com> 1.6.4-1mdk
- 1.6.4

* Sat Apr 02 2005 Olivier Blin <oblin@mandrakesoft.com> 1.5.8-3mdk
- Patch1: do not build against old freeipmi (and readline)
- fix summary ended with dot

* Wed Mar 16 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.5.8-2mdk
- don't try to build on ppc (depends on freeipmi)

* Thu Mar 03 2005 Erwan Velu <erwan@seanodes.com> 1.5.8-1mdk
- 1.5.8

* Thu Aug 19 2004 Erwan Velu <erwan@mandrakesoft.com> 1.4.8-1mdk
- Initial release

