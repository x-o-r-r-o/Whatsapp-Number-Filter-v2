# whatsapp_filter/__main__.py
from pathlib import Path

from .cli import (
    build_arg_parser,
    collect_cli_overrides,
    print_cli_examples,
    run_setup,
    run_config_menu_only,
    run_from_config,
)
from .config import load_config_file, merge_config


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.show_examples:
        print_cli_examples()
        return

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (Path.cwd() / config_path).resolve()

    if args.setup:
        cfg = run_setup(config_path=config_path)
        if args.auto_run_after_setup and cfg is not None:
            from .logger import info
            info("Auto-running app after successful setup...")
            run_from_config(cfg)
        return

    if args.config_menu:
        run_config_menu_only(config_path=config_path)
        return

    config_data = load_config_file(config_path)
    cli_overrides = collect_cli_overrides(args)
    cfg = merge_config(config_data, cli_overrides)
    run_from_config(cfg)


if __name__ == "__main__":
    main()