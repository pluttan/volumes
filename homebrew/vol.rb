class Vol < Formula
  desc "Universal build tool with beautiful terminal output"
  homepage "https://github.com/pluttan/volumes"
  url "https://github.com/pluttan/volumes/releases/download/v2.0.23/vol"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  version "2.0.23"

  resource "zsh_completion" do
    url "https://github.com/pluttan/volumes/releases/download/v2.0.23/_vol"
    sha256 "PLACEHOLDER_ZSH_SHA256"
  end

  resource "bash_completion" do
    url "https://github.com/pluttan/volumes/releases/download/v2.0.23/vol.bash"
    sha256 "PLACEHOLDER_BASH_SHA256"
  end

  resource "fish_completion" do
    url "https://github.com/pluttan/volumes/releases/download/v2.0.23/vol.fish"
    sha256 "PLACEHOLDER_FISH_SHA256"
  end

  def install
    bin.install "vol"
    
    resource("zsh_completion").stage do
      zsh_completion.install "_vol"
    end
    
    resource("bash_completion").stage do
      bash_completion.install "vol.bash" => "vol"
    end
    
    resource("fish_completion").stage do
      fish_completion.install "vol.fish"
    end
  end

  test do
    system "#{bin}/vol", "--version"
  end
end
