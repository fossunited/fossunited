with import <nixpkgs> {};
let
  pypkgs = (python311.withPackages ((ps: with ps; [
	# for nix packaged python package
	# numpy
  ])));

in
  pkgs.mkShell {

	nativeBuildInputs = [ pkgs.bashInteractive ];

	buildInputs = with pkgs; [
	  # pypkgs
	  # ruff black
	  # ty basedpyright # some are from uv itself
	  # JS lint/format tools (oxlint, oxfmt, eslint, prettier) come from node_modules
	  # via yarn, so editors and scripts share one pinned version.
	  uv nodejs yarn html-tidy
	  vale harper
    # bruno bruno-cli
	];

  }
