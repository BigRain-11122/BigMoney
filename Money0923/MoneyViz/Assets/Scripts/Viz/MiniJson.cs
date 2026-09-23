// MoneyViz · 轻量 JSON 解析器（state/state.json 为动态嵌套结构，JsonUtility 无法处理）
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace MoneyViz
{
    public static class MiniJson
    {
        public static object Parse(string json)
        {
            int i = 0;
            return ParseValue(json, ref i);
        }

        static void SkipWs(string s, ref int i)
        {
            // 注意：不能跳过逗号——逗号是对象/数组的分隔符，由调用方消费（此前误把逗号当空白导致每个对象只解析出第一个键）
            while (i < s.Length && (s[i] == ' ' || s[i] == '\n' || s[i] == '\r' || s[i] == '\t'))
                i++;
        }

        static object ParseValue(string s, ref int i)
        {
            SkipWs(s, ref i);
            if (i >= s.Length) return null;
            char c = s[i];
            if (c == '{') return ParseObj(s, ref i);
            if (c == '[') return ParseArr(s, ref i);
            if (c == '"') return ParseStr(s, ref i);
            if (c == 't') { i += 4; return true; }
            if (c == 'f') { i += 5; return false; }
            if (c == 'n') { i += 4; return null; }
            return ParseNum(s, ref i);
        }

        static Dictionary<string, object> ParseObj(string s, ref int i)
        {
            var d = new Dictionary<string, object>();
            i++; SkipWs(s, ref i);
            if (i < s.Length && s[i] == '}') { i++; return d; }
            while (i < s.Length)
            {
                SkipWs(s, ref i);
                if (i >= s.Length || s[i] == '}') { i++; break; }
                string k = ParseStr(s, ref i);
                SkipWs(s, ref i);
                if (i < s.Length && s[i] == ':') i++;
                d[k] = ParseValue(s, ref i);
                SkipWs(s, ref i);
                if (i < s.Length && s[i] == '}') { i++; break; }
                if (i < s.Length && s[i] == ',') { i++; continue; }
                break;
            }
            return d;
        }

        static List<object> ParseArr(string s, ref int i)
        {
            var l = new List<object>();
            i++; SkipWs(s, ref i);
            if (i < s.Length && s[i] == ']') { i++; return l; }
            while (i < s.Length)
            {
                SkipWs(s, ref i);
                if (i >= s.Length || s[i] == ']') { i++; break; }
                l.Add(ParseValue(s, ref i));
                SkipWs(s, ref i);
                if (i < s.Length && s[i] == ']') { i++; break; }
                if (i < s.Length && s[i] == ',') { i++; continue; }
                break;
            }
            return l;
        }

        static string ParseStr(string s, ref int i)
        {
            if (i >= s.Length || s[i] != '"') return "";
            i++;
            var sb = new StringBuilder();
            while (i < s.Length)
            {
                char c = s[i++];
                if (c == '"') break;
                if (c == '\\' && i < s.Length)
                {
                    char e = s[i++];
                    if (e == 'u' && i + 4 <= s.Length)
                    {
                        sb.Append((char)System.Convert.ToInt32(s.Substring(i, 4), 16));
                        i += 4;
                    }
                    else if (e == 'n') sb.Append('\n');
                    else if (e == 't') sb.Append('\t');
                    else sb.Append(e);
                }
                else sb.Append(c);
            }
            return sb.ToString();
        }

        static double ParseNum(string s, ref int i)
        {
            int st = i;
            while (i < s.Length && (char.IsDigit(s[i]) || s[i] == '-' || s[i] == '+' || s[i] == '.' || s[i] == 'e' || s[i] == 'E'))
                i++;
            double v;
            double.TryParse(s.Substring(st, i - st), NumberStyles.Float, CultureInfo.InvariantCulture, out v);
            return v;
        }

        // ---------------- 取值助手 ----------------
        public static Dictionary<string, object> Obj(object o) { return o as Dictionary<string, object>; }
        public static List<object> Arr(object o) { return o as List<object>; }

        /// <summary>安全取子对象（字典不存在该键返回 null）</summary>
        public static object ObjOr(Dictionary<string, object> d, string key)
        {
            if (d == null) return null;
            object v;
            return d.TryGetValue(key, out v) ? v : null;
        }

        public static string Str(object o, string def = "")
        {
            if (o == null) return def;
            if (o is string s) return s;
            return o.ToString();
        }

        public static double Num(object o, double def = 0)
        {
            if (o is double d) return d;
            if (o is bool b) return b ? 1 : 0;
            if (o is string s)
            {
                double v;
                if (double.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out v)) return v;
            }
            return def;
        }

        public static int Int(object o, int def = 0)
        {
            double v = Num(o, def);
            if (v > int.MaxValue) return int.MaxValue;
            if (v < int.MinValue) return int.MinValue;
            return (int)v;
        }

        public static bool Bool(object o, bool def = false)
        {
            if (o is bool b) return b;
            if (o is double d) return d != 0;
            if (o is string s) return s == "True" || s == "true";
            return def;
        }
    }
}
