%global jar_version 1.4
%global lh_version 1.1
%global id_version 1.1

Name:		apache-resource-bundles
Version:	2
Release:	8
Summary:	Apache Resource Bundles

Group:		Development/Java
License:	ASL 2.0
URL:		http://repo1.maven.org/maven2/org/apache/apache-resource-bundles/
Source0:	http://repo1.maven.org/maven2/org/apache/%{name}/%{version}/%{name}-%{version}.pom
Source1:	http://repo1.maven.org/maven2/org/apache/apache-jar-resource-bundle/%{jar_version}/apache-jar-resource-bundle-%{jar_version}-sources.jar
Source2:	http://repo1.maven.org/maven2/org/apache/apache-jar-resource-bundle/%{jar_version}/apache-jar-resource-bundle-%{jar_version}.pom
Source3:	http://repo1.maven.org/maven2/org/apache/apache-license-header-resource-bundle/%{lh_version}/apache-license-header-resource-bundle-%{lh_version}-sources.jar
Source4:	http://repo1.maven.org/maven2/org/apache/apache-license-header-resource-bundle/%{lh_version}/apache-license-header-resource-bundle-%{lh_version}.pom
Source5:	http://repo1.maven.org/maven2/org/apache/apache-incubator-disclaimer-resource-bundle/%{id_version}/apache-incubator-disclaimer-resource-bundle-%{id_version}-sources.jar
Source6:	http://repo1.maven.org/maven2/org/apache/apache-incubator-disclaimer-resource-bundle/%{id_version}/apache-incubator-disclaimer-resource-bundle-%{id_version}.pom

# Remove maven-release plugin (not yet available on Fedora)
Patch0:		apache-resource-bundles-cleanup-poms.patch

BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	maven2
BuildRequires:	maven-compiler-plugin
BuildRequires:	maven-install-plugin
BuildRequires:	maven-jar-plugin
BuildRequires:	maven-remote-resources-plugin
BuildRequires:	maven-resources-plugin
BuildRequires:	maven-surefire-plugin
BuildRequires:  maven-site-plugin

# Requirements from the POMs
Requires:	maven-remote-resources-plugin

Requires(post):	jpackage-utils
Requires(postun): jpackage-utils

BuildArch:	noarch

%description
An archive which contains templates for generating the necessary license files
and notices for all Apache releases.

%prep
%setup -c -T
cp %SOURCE0 ./pom.xml
%patch0 -p1

# jar
mkdir -p apache-jar-resource-bundle
pushd apache-jar-resource-bundle
jar xvf %SOURCE1
cp %SOURCE2 ./pom.xml
mkdir -p src/main/resources
mv META-INF src/main/resources
popd

# license-header
mkdir -p apache-license-header-resource-bundle
pushd apache-license-header-resource-bundle
jar xvf %SOURCE3
cp %SOURCE4 ./pom.xml
mkdir -p src/main/resources
mv META-INF src/main/resources
popd

# incubator-disclaimer
mkdir -p apache-incubator-disclaimer-resource-bundle
pushd apache-incubator-disclaimer-resource-bundle
jar xvf %SOURCE5
cp %SOURCE6 ./pom.xml
mkdir -p src/main/resources
mv META-INF src/main/resources
popd


%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp \
	-Dmaven.repo.local=$MAVEN_REPO_LOCAL \
	install

%install
rm -rf $RPM_BUILD_ROOT

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}

# jar
# 
pushd apache-jar-resource-bundle
install -m 644 \
	target/apache-jar-resource-bundle-%{jar_version}.jar \
	$RPM_BUILD_ROOT%{_javadir}/%{name}/jar-%{jar_version}.jar
cp pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-jar.pom
%add_to_maven_depmap org.apache apache-jar-resource-bundle %{jar_version} JPP/%{name} jar
popd

# license-header
pushd apache-license-header-resource-bundle
install -m 644 \
	target/apache-license-header-resource-bundle-%{lh_version}.jar \
	$RPM_BUILD_ROOT%{_javadir}/%{name}/license-header-%{lh_version}.jar
cp pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-license-header.pom
%add_to_maven_depmap org.apache apache-license-header-resource-bundle %{lh_version} JPP/%{name} license-header
popd

# incubator-disclaimer
pushd apache-incubator-disclaimer-resource-bundle
install -m 644 \
	target/apache-incubator-disclaimer-resource-bundle-%{id_version}.jar \
	$RPM_BUILD_ROOT%{_javadir}/%{name}/incubator-disclaimer-%{id_version}.jar
cp pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-incubator-disclaimer.pom
%add_to_maven_depmap org.apache apache-incubator-disclaimer-resource-bundle %{id_version} JPP/%{name} incubator-disclaimer
popd

# Unversioned jars
pushd $RPM_BUILD_ROOT%{_javadir}/%{name}
ln -sf jar-%{jar_version}.jar jar.jar
ln -sf license-header-%{lh_version}.jar license-header.jar
ln -sf incubator-disclaimer-%{id_version}.jar incubator-disclaimer.jar
popd

# Add parent to depmap too
cp pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
%add_to_maven_depmap org.apache %{name} %{version} JPP %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%{_javadir}/%{name}
%config(noreplace) %{_mavendepmapfragdir}/*
%{_mavenpomdir}/*.pom



