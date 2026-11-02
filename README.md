# Qiyu vendor archive

奇遇型号的原厂固件、DSP 资源、SDK 与配套二进制依赖的公开归档。Git 只保存按型号组织的清单、来源摘要和打包工具；压缩包存 GitHub Release。正常构建直接下载固定版本并校验，不依赖整份原厂镜像或工作站历史 build 路径。

A081 首批共 247 个文件，分为 firmware（GPU / ADSP / CDSP / SLPI / Wi-Fi / Bluetooth 及 regulatory 数据）、qvr（DSP runtime、SNPE skeleton、型号默认 config6）、controller（原厂 SDK、ARM32 Bionic DT_NEEDED 依赖和型号默认配置）、controller-dsp（3 个运行时动态加载的 SNPE 主机插件）。清单逐文件记录原来源、大小、模式与 SHA-256。快照日期不是原厂固件版本，未核实的原厂版本保持 unknown。

## 使用

在 qiyu-rootfs 中运行 `python3 tools/vendor.py fetch --output /new/vendor-cache`，下载工具当前使用 gh 登录，仓库和 Release 资产也可直接公开访问；完整四包清单为 Release 的 vendor.complete.lock.json（vendor.lock.json 保留基础三包记录）；具体固定 Release、asset 摘要和安装目标来自 devices/a081/vendor.lock.json。firmware-only 可加 `--bundle firmware`。

`python3 tools/vendor.py verify --cache /path/to/vendor-cache` 可离线逐文件核对。rootfs `assemble --vendor-cache /path/to/vendor-cache` 消费这些文件；手柄构建器也可通过 `--vendor-cache` 读取已归档的 ARM32 libc++，无需回到原镜像提取。

## 归档维护

```sh
python3 tools/package.py --source-root /path/to/curated/source-tree --output /new/release-assets
```

打包器仅接受清单中的既有文件并核对摘要，不运行原厂二进制、不提取镜像、不访问设备。发布后使用新的快照标签增加资产，不覆盖已发布快照或把二进制加入 Git。增加型号时新增 devices/<model>/catalog.json，按功能继续拆包。

每台设备的 persist / 相机与控制器校准不包含在型号公共资产包中，应在本机单独备份并注入。当前没有可靠载荷的 ctrl.zip / board.zip 不作推测收录。构建出来的 helper、shim 与开源运行时由各自源码仓库发布。

二进制保留原有权属，仓库按用户要求公开，不额外授予二进制许可；新打包工具为 GPL-3.0-or-later。归档完整性不等于制造商签名认证或拆包后的设备验收。跨仓库说明见 qiyu-docs。
