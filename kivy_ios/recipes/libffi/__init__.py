from kivy_ios.toolchain import Recipe, shprint
import sh
from os.path import exists, join


class LibffiRecipe(Recipe):
    version = "3.2.1"
    url = "https://sourceware.org/pub/libffi/libffi-{version}.tar.gz"
    library = "build/Release-{arch.sdk}/libffi.a"
    include_per_arch = True
    include_dir = "build_{arch.sdk}-{arch_arg}/include"
    include_name = "ffi"
    archs = ["x86_64", "arm64"]

    def prebuild_arch(self, arch):
        if self.has_marker("patched"):
            return
        # XCode 10 minimum is 8.0 now.
        shprint(sh.sed,
                "-i.bak",
                "s/-miphoneos-version-min=5.1.1/-miphoneos-version-min=8.0/g",
                "generate-darwin-source-and-headers.py")
        self.apply_patch("fix-win32-unreferenced-symbol.patch")
        self.apply_patch("generate-darwin-source-and-headers-python3-items.patch")
        self.set_marker("patched")

    def build_arch(self, arch):
        if exists("generate-darwin-source-and-headers.py"):
            shprint(
                sh.mv,
                "generate-darwin-source-and-headers.py",
                "_generate-darwin-source-and-headers.py")
            shprint(sh.touch, "generate-darwin-source-and-headers.py")
        python3 = sh.Command("python3")
        shprint(python3, "_generate-darwin-source-and-headers.py", "--only-ios")
        shprint(sh.xcodebuild, self.ctx.concurrent_xcodebuild,
                "ONLY_ACTIVE_ARCH=NO",
                "ARCHS={}".format("x86_64 arm64" if arch.arch == "x86_64" else arch.arch),
                "BITCODE_GENERATION_MODE=bitcode",
                "-sdk", arch.sdk,
                "-project", "libffi.xcodeproj",
                "-target", "libffi-iOS",
                "-configuration", "Release")

    def install_include(self):
        super().install_include()

        include_name = self.include_name or self.name
        src_dir = join(self.ctx.include_dir, "x86_64", include_name)
        dest_dir = join(self.ctx.include_dir, "ios-arm64-simulator")
        shprint(sh.rm, "-rf", join(dest_dir, include_name))
        shprint(sh.ln, "-s", src_dir, dest_dir)

recipe = LibffiRecipe()
