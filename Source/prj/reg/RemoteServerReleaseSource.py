
from mtm.ioc.Inject import Inject
from mtm.ioc.Inject import InjectMany
import mtm.ioc.IocAssertions as Assertions

import os
import urllib.parse
import urllib.request
from mtm.util.Assert import *
import mtm.util.YamlSerializer as YamlSerializer

import tempfile

class RemoteServerReleaseSource:
    _log = Inject('Logger')
    _sys = Inject('SystemHelper')
    _packageExtractor = Inject('UnityPackageExtractor')

    def __init__(self, manifestUrl):
        self._manifestUrl = manifestUrl
        self._releaseInfos = []

    @property
    def releases(self):
        return self._releaseInfos

    def init(self):
        with self._log.heading("Initializing remote server release source"):
            self._log.debug("Initializing remote server release source with URL '{0}'", self._manifestUrl)
            response = urllib.request.urlopen(self._manifestUrl)
            manifestData = response.read().decode('utf-8')

            self._log.debug("Got manifest with data: \n{0}".format(manifestData))

            self._manifest = YamlSerializer.deserialize(manifestData)

            for info in self._manifest.releases:
                info.url = urllib.parse.urljoin(self._manifestUrl, info.localPath)
                info.localPath = None
                self._releaseInfos.append(info)

    def getName(self):
        return "File Server"

    def installRelease(self, packageRootDir, releaseInfo, forcedName):
        assertThat(releaseInfo.url)

        try:
            with self._log.heading("Downloading release from url '{0}'".format(releaseInfo.url)):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.unitypackage') as tempFile:
                    tempFilePath = tempFile.name

                self._log.debug("Downloading url to temporary file '{0}'".format(tempFilePath))
                urllib.request.urlretrieve(releaseInfo.url, tempFilePath)

                return self._packageExtractor.extractUnityPackage(packageRootDir, tempFilePath, releaseInfo.name, forcedName)
        finally:
            if os.path.exists(tempFilePath):
                os.remove(tempFilePath)
