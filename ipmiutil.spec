%define name    ipmiutil
%define version	2.4.1
%define release %mkrel 4

Name:       %name
Version:    %version
Release:    %release
Summary:    A package that includes various IPMI server management utilities
License:    BSD
Group:      System/Kernel and hardware
Url:	    http://ipmiutil.sourceforge.net/
Source:     http://optusnet.dl.sourceforge.net/sourceforge/ipmiutil/%{name}-%{version}.tar.gz
Patch1:         ipmiutil-2.4.1-fix-format-errors.patch
Patch2:         ipmiutil-2.4.1-fix-getline-conflict.patch
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
%patch1 -p1
%patch2 -p1

%build
%configure2_5x
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
