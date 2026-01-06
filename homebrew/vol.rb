class Vol < Formula
  desc "Universal build tool with beautiful terminal output"
  homepage "https://github.com/pluttan/volumes"
  url "https://github.com/pluttan/volumes/releases/download/v2.0.0/vol"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  version "2.0.0"

  def install
    bin.install "vol"
  end

  test do
    system "#{bin}/vol", "--version"
  end
end
