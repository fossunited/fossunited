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
	  # ty # basedpyright
	  uv nodePackages.eslint nodePackages.prettier html-tidy nodePackages.yarn
	  vale harper
	];

  }
