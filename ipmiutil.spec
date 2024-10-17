%define _disable_ld_no_undefined 1
%define _disable_rebuild_configure 1

%define libmajor 1
%define libname %mklibname ipmiutil %{libmajor}

Name:      ipmiutil
Version:	3.1.8
Release:	2
Summary:   Easy-to-use IPMI server management utilities

License:   BSD
Group:     System/Kernel and hardware
Source:    http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
URL:       https://ipmiutil.sourceforge.net
Requires:  systemd-units
BuildRequires: pkgconfig(openssl)
BuildRequires: libtool
BuildRequires: autoconf

%define unit_dir  %{_unitdir}
%define systemd_fls %{_datadir}/%{name}
%define init_dir  %{_initrddir}

%description
The ipmiutil package provides easy-to-use utilities to view the SEL,
perform an IPMI chassis reset, set up the IPMI LAN and Platform Event Filter
entries to allow SNMP alerts, Serial-Over-LAN console, event daemon, and 
other IPMI tasks.
These can be invoked with the metacommand ipmiutil, or via subcommand
shortcuts as well.  IPMIUTIL can also write sensor thresholds, FRU asset tags, 
and has a full IPMI configuration save/restore.
An IPMI driver can be provided by either the OpenIPMI driver (/dev/ipmi0)
or the Intel IPMI driver (/dev/imb), etc.  If used locally and no driver is
detected, ipmiutil will use user-space direct I/Os instead.

%package devel
Group:    Development/C
Summary:  Includes libraries and headers for the ipmiutil package

Provides: ipmiutil-static = %{version}-%{release}
Requires: %libname = %{version}-%{release}

%description devel
The ipmiutil-devel package contains headers and libraries which are
useful for building custom IPMI applications.

%prep
%autosetup -p1
%configure

%build
%make_build

%install
%make_install

%files
%dir %{_datadir}/%{name}
%dir %{_var}/lib/%{name}
%{_bindir}/ipmiutil
%{_bindir}/idiscover
%{_bindir}/ievents
%{_sbindir}/ipmi_port
%{_sbindir}/ialarms 
%{_sbindir}/iconfig
%{_sbindir}/icmd 
%{_sbindir}/ifru 
%{_sbindir}/igetevent 
%{_sbindir}/ihealth 
%{_sbindir}/ilan 
%{_sbindir}/ireset 
%{_sbindir}/isel 
%{_sbindir}/iseltime
%{_sbindir}/isensor 
%{_sbindir}/iserial 
%{_sbindir}/isol 
%{_sbindir}/iuser
%{_sbindir}/iwdt 
%{_sbindir}/ipicmg 
%{_sbindir}/ifirewall 
%{_sbindir}/ifwum 
%{_sbindir}/ihpm 
%{_datadir}/%{name}/ipmiutil_evt
%{_datadir}/%{name}/ipmiutil_asy
%{_datadir}/%{name}/ipmiutil_wdt
%{_datadir}/%{name}/ipmi_port
%{_datadir}/%{name}/ipmi_info
%{_datadir}/%{name}/checksel
%{systemd_fls}/ipmiutil_evt.service
%{systemd_fls}/ipmiutil_asy.service
%{systemd_fls}/ipmiutil_wdt.service
%{systemd_fls}/ipmi_port.service
%{_datadir}/%{name}/ipmiutil.pre
%{_datadir}/%{name}/ipmiutil.setup
%{_datadir}/%{name}/ipmi_if.sh
%{_datadir}/%{name}/evt.sh
%{_datadir}/%{name}/ipmi.init.basic
%{_datadir}/%{name}/bmclanpet.mib
%{_mandir}/man?/*
%doc AUTHORS ChangeLog COPYING NEWS README TODO 
%doc doc/UserGuide

%libpackage ipmiutil %libmajor

%files devel
# %{_datadir}/%{name} is used by both ipmiutil and ipmituil-devel
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/ipmi_sample.c
%{_datadir}/%{name}/ipmi_sample_evt.c
%{_datadir}/%{name}/isensor.c
%{_datadir}/%{name}/ievents.c
%{_datadir}/%{name}/isensor.h
%{_datadir}/%{name}/ievents.h
%{_datadir}/%{name}/Makefile
%{_datadir}/%{name}/ipmiutil.env.template
%{_includedir}/ipmicmd.h
%{_libdir}/libipmiutil.so
%{_libdir}/libipmiutil.a

%post
# POST_INSTALL, $1 = 1 if rpm -i, $1 = 2 if rpm -U

if [ "$1" = "1" ]
then
   # doing rpm -i, first time
   vardir=%{_var}/lib/%{name}
   scr_dir=%{_datadir}/%{name}

   if [ -x /bin/systemctl ]; then
      echo "IINITDIR=%{init_dir}" >>%{_datadir}/%{name}/ipmiutil.env
      cp -f ${scr_dir}/ipmiutil_evt.service %{unit_dir}
      cp -f ${scr_dir}/ipmiutil_asy.service %{unit_dir}
      cp -f ${scr_dir}/ipmiutil_wdt.service %{unit_dir}
      cp -f ${scr_dir}/ipmi_port.service    %{unit_dir}
      # systemctl enable ipmi_port.service >/dev/null 2>&1 || :
   else 
      cp -f ${scr_dir}/ipmiutil_wdt %{init_dir}
      cp -f ${scr_dir}/ipmiutil_asy %{init_dir}
      cp -f ${scr_dir}/ipmiutil_evt %{init_dir}
      cp -f ${scr_dir}/ipmi_port    %{init_dir}
      cp -f ${scr_dir}/ipmi_info    %{init_dir}
   fi

   # Run some ipmiutil command to see if any IPMI interface works.
   %{_bindir}/ipmiutil sel -v >/dev/null 2>&1
   IPMIret=$?

   # If IPMIret==0, the IPMI cmd was successful, and IPMI is enabled locally.
   if [ $IPMIret -eq 0 ]; then
      # If IPMI is enabled, automate managing the IPMI SEL
      if [ -d %{_sysconfdir}/cron.daily ]; then
         cp -f %{_datadir}/%{name}/checksel %{_sysconfdir}/cron.daily
      fi
      # IPMI_IS_ENABLED, so enable services, but only if Red Hat
      if [ -f /etc/redhat-release ]; then
         if [ -x /bin/systemctl ]; then
            touch ${scr_dir}/ipmi_port.service
         elif [ -x /sbin/chkconfig ]; then
            /sbin/chkconfig --add ipmi_port
            /sbin/chkconfig --add ipmiutil_wdt
            /sbin/chkconfig --add ipmiutil_evt 
            /sbin/chkconfig --add ipmi_info
         fi
      fi
   
      # Capture a snapshot of IPMI sensor data once now for later reuse.
      sensorout=$vardir/sensor_out.txt
      if [ ! -f $sensorout ]; then
         %{_bindir}/ipmiutil sensor -q >$sensorout
      fi
   fi
else
   # postinstall, doing rpm update
   %{_bindir}/ipmiutil sel -v >/dev/null 2>&1
   if [ $? -eq 0 ]; then
      if [ -d %{_sysconfdir}/cron.daily ]; then
         cp -f %{_datadir}/%{name}/checksel %{_sysconfdir}/cron.daily
      fi
   fi
fi
%systemd_post  ipmiutil_evt.service
%systemd_post  ipmiutil_asy.service
%systemd_post  ipmiutil_wdt.service
%systemd_post  ipmi_port.service

%preun
# before uninstall,  $1 = 1 if rpm -U, $1 = 0 if rpm -e
if [ "$1" = "0" ]
then
   if [ -x /bin/systemctl ]; then
     if [ -f %{unit_dir}/ipmiutil_evt.service ]; then
%systemd_preun  ipmiutil_evt.service
%systemd_preun  ipmiutil_asy.service
%systemd_preun  ipmiutil_wdt.service
%systemd_preun  ipmi_port.service
     fi
   else 
     if [ -x /sbin/service ]; then
        /sbin/service ipmi_port stop       >/dev/null 2>&1
        /sbin/service ipmiutil_wdt stop    >/dev/null 2>&1
        /sbin/service ipmiutil_asy stop    >/dev/null 2>&1
        /sbin/service ipmiutil_evt stop    >/dev/null 2>&1
     fi
     if [ -x /sbin/chkconfig ]; then
        /sbin/chkconfig --del ipmi_port    >/dev/null 2>&1
        /sbin/chkconfig --del ipmiutil_wdt >/dev/null 2>&1
        /sbin/chkconfig --del ipmiutil_asy >/dev/null 2>&1
        /sbin/chkconfig --del ipmiutil_evt >/dev/null 2>&1
     fi
   fi
   if [ -f %{_sysconfdir}/cron.daily/checksel ]; then
        rm -f %{_sysconfdir}/cron.daily/checksel
   fi
fi

%postun
if [ -x /bin/systemctl ]; then
%systemd_postun_with_restart  ipmi_port.service
   if [ -f %{unit_dir}/ipmiutil_evt.service ]; then
      rm -f %{unit_dir}/ipmiutil_evt.service 
      rm -f %{unit_dir}/ipmiutil_asy.service 
      rm -f %{unit_dir}/ipmiutil_wdt.service 
      rm -f %{unit_dir}/ipmi_port.service    
   fi
else
   if [ -f %{init_dir}/ipmiutil_evt.service ]; then
      rm -f %{init_dir}/ipmiutil_wdt 2>/dev/null
      rm -f %{init_dir}/ipmiutil_asy 2>/dev/null
      rm -f %{init_dir}/ipmiutil_evt 2>/dev/null
      rm -f %{init_dir}/ipmi_port    2>/dev/null
   fi
fi
