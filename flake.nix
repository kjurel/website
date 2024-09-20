# https://github.com/NixOS/nix/issues/6140#issuecomment-1986317698
{
  description = "website flake";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };
  outputs =
    { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages."x86_64-linux";
    in
    {
      formatter."x86_64-linux" = pkgs.nixfmt-rfc-style;
      devShells."x86_64-linux".default = pkgs.mkShell {
        packages = with pkgs; [
          statix
          nodejs
          pnpm
          mypy
          python3
          python312Packages.pre-commit-hooks
          prettierd
          eslint_d
        ];
        ASTRO_TELEMETRY_DISABLED = 1;
      };
    };
}

